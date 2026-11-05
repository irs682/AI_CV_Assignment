"""Safety and data tests; never saves approval records in the real dataset."""
from pathlib import Path
import json
import io
import tempfile
import unittest
from unittest.mock import patch
import sys
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from annotation_tool.server import AnnotationRequestHandler, with_proposals
from models.training_pipeline import preflight, load_pair
from dataset.refine_all_masks import self_intersects

class Stage3Safety(unittest.TestCase):
    def test_training_refuses_current_unapproved_dataset(self):
        config=json.loads((ROOT/'models/unet_laptop.json').read_text())
        with self.assertRaisesRegex(RuntimeError,'human approval and verified mask required'):
            preflight(config)

    def test_api_rejects_implicit_approval_without_writing(self):
        handler=object.__new__(AnnotationRequestHandler)
        before=(ROOT/'dataset/annotation_review_log.json').read_bytes()
        for payload in [dict(name='notebook_003'),dict(name='notebook_003',inspected=True,verified_by='test',status='automatically_proposed')]:
            self.assertFalse(handler._save_verified_mask(payload)['success'])
        self.assertEqual(before,(ROOT/'dataset/annotation_review_log.json').read_bytes())

    def test_existing_human_work_is_not_replaced(self):
        # In-memory test record, not a saved review or approval.
        original=dict(name='notebook_003',status='unresolved',polygon_vertices=[[1,1],[9,1],[4,9]],reviewer_notes='Human working notes')
        merged=with_proposals([original.copy()])[0]
        self.assertEqual(merged['polygon_vertices'],original['polygon_vertices'])
        self.assertEqual(merged['reviewer_notes'],original['reviewer_notes'])

    def test_letterbox_keeps_binary_mask_and_aspect_ratio(self):
        image=np.full((100,200,3),100,np.uint8); mask=np.zeros((100,200),np.uint8); mask[10:90,20:180]=255
        with patch('models.training_pipeline.cv2.imread',side_effect=[image,mask]):
            x,y=load_pair('fixture',256)
            self.assertEqual(x.shape,(3,256,256));self.assertEqual(y.shape,(1,256,256))
            self.assertEqual(set(np.unique(y)),{0.,1.});self.assertEqual(float(x[:,:64].sum()),0.)

    def test_polygon_qc_detects_crossing(self):
        self.assertTrue(self_intersects([[0,0],[10,10],[0,10],[10,0]]))
        self.assertFalse(self_intersects([[0,0],[10,0],[10,10],[0,10]]))

    def test_work_backup_never_records_inspection_or_approval(self):
        handler=object.__new__(AnnotationRequestHandler)
        payload=dict(name='notebook_001',polygon=[[1,1],[9,1],[4,9]],inspected=True,
                     status='manually_verified',verified_by='not a real review')
        with patch('annotation_tool.server.os.path.exists',return_value=False):
            self.assertFalse(handler._save_work(payload)['success'])
        written=[]
        def exists(path): return str(path).endswith('.jpg')
        with patch('annotation_tool.server.os.path.exists',side_effect=exists),patch('annotation_tool.server.atomic_json',side_effect=lambda p,d:written.append(d)):
            result=handler._save_work(payload)
        self.assertTrue(result['success']);self.assertFalse(result['approved'])
        record=written[0]['notebook_001']
        self.assertFalse(any(k in record for k in ['status','inspected_at','inspected_by','verified_at','verified_by']))

    def test_existing_verified_mask_cannot_be_overwritten(self):
        handler=object.__new__(AnnotationRequestHandler)
        result=handler._save_verified_mask(dict(name='notebook_003',inspected=True,verified_by='test',status='manually_verified'))
        self.assertFalse(result['success']);self.assertIn('protected',result['error'])

    def test_approval_write_and_readback_use_mock_storage_only(self):
        handler=object.__new__(AnnotationRequestHandler)
        payload=dict(name='notebook_001',polygon=[[1,1],[8,1],[8,8],[1,8]],inspected=True,
                     verified_by='Isolated test fixture',status='manually_verified')
        image=np.zeros((10,10,3),np.uint8); mask=np.zeros((10,10),np.uint8);mask[1:9,1:9]=255
        def read_image(path,*args): return mask.copy() if str(path).endswith('.tmp.png') else image.copy()
        def fake_open(path,*args,**kwargs):
            if str(path).endswith('annotation_review_log.json'):
                return io.StringIO(json.dumps([{'name':'notebook_001'}]))
            return io.BytesIO(b'fixture PNG bytes')
        from annotation_tool import server
        with patch.object(server.os.path,'exists',side_effect=lambda p:str(p)==server.LOG_JSON),patch.object(server.cv2,'imread',side_effect=read_image),patch.object(server.cv2,'imwrite',return_value=True),patch.object(server.os,'replace'),patch.object(server.os,'makedirs'),patch('builtins.open',side_effect=fake_open),patch.object(server,'atomic_json') as write,patch.object(server,'write_markdown_log'),patch.object(server,'generate_qc_contact_sheet',return_value={'valid':True}):
            result=handler._save_verified_mask(payload)
        self.assertTrue(result['success']);self.assertEqual(write.call_count,1)

    def test_png_write_failure_never_records_approval(self):
        from annotation_tool import server
        handler=object.__new__(AnnotationRequestHandler)
        with patch.object(server.os.path,'exists',return_value=False),patch.object(server.cv2,'imread',return_value=np.zeros((10,10,3),np.uint8)),patch.object(server.cv2,'imwrite',return_value=False),patch.object(server.os,'makedirs'),patch.object(server,'atomic_json') as write:
            result=handler._save_verified_mask(dict(name='notebook_001',polygon=[[1,1],[8,1],[8,8],[1,8]],inspected=True,verified_by='Isolated fixture',status='manually_verified'))
        self.assertFalse(result['success']);write.assert_not_called()

if __name__=='__main__': unittest.main()
