"""Calibrate camera intrinsics from the supplied checkerboard photographs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"
OUTPUT_DIR = BASE_DIR / "parameters"
DETECTED_DIR = OUTPUT_DIR / "detected_corners"
PATTERN_SIZES = ((7, 9), (9, 7))
CORNER_REFINEMENT = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001,
)
SB_FLAGS = cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_EXHAUSTIVE
CLASSIC_FLAGS = (
    cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
)


@dataclass
class Detection:
    image_path: Path
    image: np.ndarray
    corners: np.ndarray
    pattern_size: tuple[int, int]
    method: str
    attempts: dict[str, dict[str, bool]]


def detect_corners(image_path: Path) -> tuple[Detection | None, str | None]:
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        return None, "image could not be decoded"

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    candidates: list[tuple[tuple[int, int], str, np.ndarray]] = []
    attempts: dict[str, dict[str, bool]] = {}

    for pattern_size in PATTERN_SIZES:
        label = f"{pattern_size[0]}x{pattern_size[1]}"
        sb_found, sb_corners = cv2.findChessboardCornersSB(
            gray, pattern_size, SB_FLAGS
        )
        classic_found, classic_corners = cv2.findChessboardCorners(
            gray, pattern_size, CLASSIC_FLAGS
        )
        attempts[label] = {
            "sb_found": bool(sb_found),
            "classic_found": bool(classic_found),
        }

        if sb_found and sb_corners is not None:
            candidates.append((pattern_size, "SB", sb_corners))
        if classic_found and classic_corners is not None:
            candidates.append((pattern_size, "classic", classic_corners))

    if not candidates:
        return None, "no complete 7x9 or 9x7 corner grid detected"

    # Prefer the stated 7x9 layout and SB localization, with classic fallback.
    pattern_rank = {size: rank for rank, size in enumerate(PATTERN_SIZES)}
    method_rank = {"SB": 0, "classic": 1}
    pattern_size, method, corners = min(
        candidates,
        key=lambda item: (
            pattern_rank[item[0]],
            method_rank[item[1]],
        ),
    )
    refined = cv2.cornerSubPix(
        gray,
        corners,
        (11, 11),
        (-1, -1),
        CORNER_REFINEMENT,
    )
    return (
        Detection(
            image_path=image_path,
            image=image,
            corners=refined,
            pattern_size=pattern_size,
            method=method,
            attempts=attempts,
        ),
        None,
    )


def make_object_points(pattern_size: tuple[int, int]) -> np.ndarray:
    columns, rows = pattern_size
    points = np.zeros((columns * rows, 3), dtype=np.float32)
    points[:, :2] = np.mgrid[0:columns, 0:rows].T.reshape(-1, 2)
    return points


def write_image(path: Path, image: np.ndarray) -> None:
    if not cv2.imwrite(str(path), image):
        raise OSError(f"Could not write image: {path}")


def save_detected_corners(detection: Detection) -> Path:
    output_path = DETECTED_DIR / f"{detection.image_path.stem}_corners.jpg"
    annotated = detection.image.copy()
    cv2.drawChessboardCorners(
        annotated, detection.pattern_size, detection.corners, True
    )
    write_image(output_path, annotated)
    return output_path


def save_undistortion_comparison(
    detection: Detection,
    camera_matrix: np.ndarray,
    distortion_coefficients: np.ndarray,
    image_size: tuple[int, int],
) -> Path:
    width, height = image_size
    new_camera_matrix, _ = cv2.getOptimalNewCameraMatrix(
        camera_matrix,
        distortion_coefficients,
        image_size,
        1,
        image_size,
    )
    undistorted = cv2.undistort(
        detection.image,
        camera_matrix,
        distortion_coefficients,
        None,
        new_camera_matrix,
    )
    before = detection.image.copy()
    after = undistorted.copy()
    cv2.putText(
        before,
        "Before",
        (24, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        after,
        "After",
        (24, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 128, 0),
        2,
        cv2.LINE_AA,
    )
    comparison = np.hstack((before, after))
    output_path = OUTPUT_DIR / (
        f"undistortion_comparison_{width}x{height}.jpg"
    )
    write_image(output_path, comparison)
    return output_path


def calibrate_group(
    detections: list[Detection],
    image_size: tuple[int, int],
) -> dict[str, Any]:
    object_points = [
        make_object_points(detection.pattern_size) for detection in detections
    ]
    image_points = [detection.corners for detection in detections]
    rms, camera_matrix, distortion, rotation_vectors, translation_vectors = (
        cv2.calibrateCamera(
            object_points,
            image_points,
            image_size,
            None,
            None,
        )
    )

    image_errors: list[dict[str, Any]] = []
    squared_error_sum = 0.0
    point_count = 0
    for detection, obj, observed, rotation, translation in zip(
        detections,
        object_points,
        image_points,
        rotation_vectors,
        translation_vectors,
    ):
        projected, _ = cv2.projectPoints(
            obj, rotation, translation, camera_matrix, distortion
        )
        residuals = observed.reshape(-1, 2) - projected.reshape(-1, 2)
        error = float(np.sqrt(np.mean(np.sum(residuals**2, axis=1))))
        squared_error_sum += float(np.sum(residuals**2))
        point_count += len(residuals)
        image_errors.append(
            {
                "image": detection.image_path.name,
                "reprojection_error_px": error,
                "corner_detector": detection.method,
                "pattern_size_columns_rows": list(detection.pattern_size),
            }
        )

    width, height = image_size
    model_path = OUTPUT_DIR / f"camera_parameters_{width}x{height}.npz"
    np.savez_compressed(
        model_path,
        camera_matrix=camera_matrix,
        distortion_coefficients=distortion,
        image_size_wh=np.array(image_size, dtype=np.int32),
        pattern_size_columns_rows=np.array(detections[0].pattern_size),
        square_size_units="unit square",
        rms_reprojection_error_px=rms,
    )
    comparison_path = save_undistortion_comparison(
        detections[0], camera_matrix, distortion, image_size
    )

    return {
        "image_size_px": {"width": width, "height": height},
        "image_count": len(detections),
        "corner_count_per_image": len(object_points[0]),
        "rms_reprojection_error_px": float(rms),
        "mean_individual_reprojection_error_px": float(
            np.mean(
                [
                    record["reprojection_error_px"]
                    for record in image_errors
                ]
            )
        ),
        "max_individual_reprojection_error_px": max(
            record["reprojection_error_px"] for record in image_errors
        ),
        "camera_matrix": camera_matrix.tolist(),
        "distortion_coefficients": distortion.reshape(-1).tolist(),
        "parameters_file": str(model_path.relative_to(BASE_DIR)),
        "undistortion_comparison_file": str(
            comparison_path.relative_to(BASE_DIR)
        ),
        "individual_image_errors": image_errors,
        "squared_error_sum": squared_error_sum,
        "point_count": point_count,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DETECTED_DIR.mkdir(parents=True, exist_ok=True)
    images = sorted(
        path
        for path in IMAGE_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg"}
    )
    if not images:
        raise FileNotFoundError(f"No JPG images found in {IMAGE_DIR}")

    print(f"Input images: {len(images)} ({IMAGE_DIR})")
    detections: list[Detection] = []
    failures: list[dict[str, str]] = []
    source_sizes: dict[str, int] = defaultdict(int)
    for image_path in images:
        detection, failure = detect_corners(image_path)
        if detection is None:
            reason = failure or "unknown detection failure"
            print(f"FAILED  {image_path.name}: {reason}")
            failures.append({"image": image_path.name, "reason": reason})
            continue

        height, width = detection.image.shape[:2]
        source_sizes[f"{width}x{height}"] += 1
        overlay_path = save_detected_corners(detection)
        attempt_summary = "; ".join(
            f"{size}: SB={'yes' if result['sb_found'] else 'no'}, "
            f"classic={'yes' if result['classic_found'] else 'no'}"
            for size, result in detection.attempts.items()
        )
        print(
            f"SUCCESS {image_path.name}: "
            f"{detection.pattern_size[0]}x{detection.pattern_size[1]}, "
            f"{detection.method}, 63 corners; {attempt_summary}; "
            f"saved {overlay_path.relative_to(BASE_DIR)}"
        )
        detections.append(detection)

    if not detections:
        raise RuntimeError("No checkerboards were detected; calibration stopped.")

    grouped: dict[tuple[int, int], list[Detection]] = defaultdict(list)
    for detection in detections:
        height, width = detection.image.shape[:2]
        grouped[(width, height)].append(detection)

    group_results = [
        calibrate_group(group_detections, image_size)
        for image_size, group_detections in sorted(grouped.items())
    ]
    total_squared_error = sum(
        result["squared_error_sum"] for result in group_results
    )
    total_point_count = sum(result["point_count"] for result in group_results)
    overall_rms = float(np.sqrt(total_squared_error / total_point_count))
    for result in group_results:
        result.pop("squared_error_sum")
        result.pop("point_count")

    csv_path = OUTPUT_DIR / "per_image_reprojection_errors.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=(
                "image",
                "image_size_px",
                "reprojection_error_px",
                "corner_detector",
                "pattern_size_columns_rows",
            ),
        )
        writer.writeheader()
        for result in group_results:
            size = result["image_size_px"]
            size_label = f"{size['width']}x{size['height']}"
            for record in result["individual_image_errors"]:
                writer.writerow(
                    {
                        **record,
                        "image_size_px": size_label,
                        "pattern_size_columns_rows": "x".join(
                            str(value)
                            for value in record["pattern_size_columns_rows"]
                        ),
                    }
                )

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "opencv_version": cv2.__version__,
        "numpy_version": np.__version__,
        "input_directory": str(IMAGE_DIR.relative_to(BASE_DIR)),
        "input_image_count": len(images),
        "detected_image_count": len(detections),
        "failed_images": failures,
        "source_image_sizes_px": dict(sorted(source_sizes.items())),
        "checkerboard": {
            "internal_corners": [7, 9],
            "tested_pattern_sizes_columns_rows": [
                list(size) for size in PATTERN_SIZES
            ],
            "object_point_order": (
                "row-major for the chosen (columns, rows) pattern size"
            ),
            "square_size": 1.0,
            "square_size_units": "unit square; arbitrary scale",
            "physical_square_size_measured_or_verified": False,
            "corner_refinement": {
                "method": "cv2.cornerSubPix",
                "window": [11, 11],
                "zero_zone": [-1, -1],
                "criteria_max_iterations": 30,
                "criteria_epsilon": 0.001,
            },
        },
        "overall_pooled_rms_reprojection_error_px": overall_rms,
        "overall_rms_note": (
            "Pooled over all detected corners after fitting separate camera "
            "models for each source resolution; it is not one shared model."
        ),
        "calibrations_by_resolution": group_results,
        "quality_assessment": {
            "resolution": (
                "The supplied files are 1500x1125 or 1500x2000 pixels and "
                "each successful image contributes 63 corners. Resolution "
                "supports detection, but alone does not guarantee precise "
                "calibration."
            ),
            "observed_quality": (
                "Corner detection succeeded for the listed inputs. The "
                "1500x2000 cohort has a larger RMS and checkerboard_002.jpg "
                "has a high per-image reprojection error; inspect its saved "
                "corner overlay before relying on that cohort for precision."
            ),
            "source_limitations": (
                "These are the supplied JPG photographs of a checkerboard "
                "shown on a laptop display. Visible screen pixel structure, "
                "moire, display brightness variation, glare, focus blur, and "
                "perspective can shift corner locations. If the JPGs were "
                "extracted from PDFs, prior resizing, resampling, cropping, "
                "and JPEG compression may further limit geometric accuracy; "
                "the extraction history cannot be independently established "
                "from these files."
            ),
            "metric_scale": (
                "Unit-square coordinates calibrate intrinsics only up to the "
                "chosen arbitrary pattern scale. They do not establish "
                "physical square size or metric object dimensions."
            ),
        },
        "outputs": {
            "metadata": "calibration_metadata.json",
            "per_image_errors": "per_image_reprojection_errors.csv",
            "detected_corner_images": "detected_corners/",
        },
    }
    metadata_path = OUTPUT_DIR / "calibration_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    print("\nCalibration results")
    print(f"Successful detections: {len(detections)}/{len(images)}")
    print(f"Failed detections: {len(failures)}")
    print("Resolution cohorts:")
    for result in group_results:
        size = result["image_size_px"]
        print(
            f"  {size['width']}x{size['height']}: "
            f"{result['image_count']} images, "
            f"RMS={result['rms_reprojection_error_px']:.6f} px, "
            f"mean per-image={result['mean_individual_reprojection_error_px']:.6f} px, "
            f"max per-image={result['max_individual_reprojection_error_px']:.6f} px"
        )
    print(f"Overall pooled RMS reprojection error: {overall_rms:.6f} px")
    if failures:
        print("Failed images:")
        for failure in failures:
            print(f"  {failure['image']}: {failure['reason']}")
    print("Saved files:")
    print(f"  {metadata_path}")
    print(f"  {csv_path}")
    for result in group_results:
        print(f"  {BASE_DIR / result['parameters_file']}")
        print(f"  {BASE_DIR / result['undistortion_comparison_file']}")
    print(f"  {DETECTED_DIR} ({len(detections)} images)")


if __name__ == "__main__":
    main()