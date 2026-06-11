import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dto import GridDTO


class TestConfig(unittest.TestCase):
    
    def test_validate_county(self):
         
            records = [
                {"CoListAgentDirectPhone": "123-456-7890", "CountyOrParish": "Seminole"},   
                {"CoListAgentDirectPhone": "987-654-3210", "CountyOrParish": "Orange"},   
                {"CoListAgentDirectPhone": "987-654-3210", "CountyOrParish": "invalidcounty"},
                {"CoListAgentDirectPhone": "987-654-3210", "CountyOrParish":   None}         
            ]
            
            valid, invalid = GridDTO.process_records_batch(records)
            
            # Counts are correct!
            self.assertEqual(len(valid), 2)
            self.assertEqual(len(invalid), 2)
            
           
            error_messages = [str(inv["error"]) for inv in invalid]
            
            # Assert that both expected error types exist somewhere in the failures
            self.assertTrue(any("Invalid county" in err for err in error_messages), "Custom 'Invalid county' error missing!")
            self.assertTrue(any("Input should be a valid string" in err for err in error_messages), "Pydantic 'NoneType' error missing!")
    
    
    def test_process_records_batch(self):
        # Test with valid records
        records = [
            {"CoListAgentDirectPhone": "123-456-7890", "CountyOrParish": "Seminole"},
            {"CoListAgentDirectPhone": "987-654-3210", "CountyOrParish": "Orange"},
            {"CoListAgentDirectPhone": "555-555-5555", "ListPrice": "Invalidlistprice", "MFR_CurrentPrice": "500.00"},
            {"CoListAgentDirectPhone": "555-555-5555", "ListPrice": 250.00, "MFR_CurrentPrice": 500.00},
            {}
        ]
        valid, invalid = GridDTO.process_records_batch(records)
        self.assertEqual(len(valid), 4)
        self.assertEqual(len(invalid), 1)
        self.assertIn("Input should be a valid number", str(invalid[0]["error"]))

    def test_fields(self):
        
        all_annotations = GridDTO.process_records_batch.__annotations__.keys()
        ignored_keys = {'records', 'return'}
        python_fields = {field for field in all_annotations if field not in ignored_keys}
        
        bq_fields = {schema_field.name for schema_field in GridDTO.bq_schema()}
        
        missing_fields = python_fields - bq_fields
        
        self.assertEqual(
            missing_fields, 
            set(), 
            msg=f"The following Python fields are missing from the BigQuery schema: {missing_fields}"
        )

if __name__ == "__main__":
    unittest.main()