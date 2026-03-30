import great_expectations as gx
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_validation(cleaned_path: str, context_root_dir: str = "expectations") -> bool:
    """
    Dynamically assesses generic baseline validity constraints.
    """
    try:
        os.makedirs(context_root_dir, exist_ok=True)
        context = gx.get_context(mode="ephemeral")
        
        datasource = context.sources.add_pandas("dynamic_datasource")
        asset = datasource.add_csv_asset(name="cleaned_dynamic_data", filepath_or_buffer=cleaned_path)
        batch_request = asset.build_batch_request()
        
        suite_name = "dynamic_validation_suite"
        context.add_or_update_expectation_suite(expectation_suite_name=suite_name)
        validator = context.get_validator(batch_request=batch_request, expectation_suite_name=suite_name)
        
        # Generic Rule 1: Not totally empty CSV
        validator.expect_table_row_count_to_be_between(min_value=1)
        
        validator.save_expectation_suite(discard_failed_expectations=False)
        checkpoint = context.add_or_update_checkpoint(
            name="dynamic_checkpoint",
            validator=validator,
            action_list=[
                {"name": "store_validation_result", "action": {"class_name": "StoreValidationResultAction"}},
            ]
        )
        result = checkpoint.run()
        
        if result.success:
            logging.info("Dynamic GE Validation PASSED.")
        else:
            logging.error("Dynamic GE Validation FAILED.")
            
        return result.success
    except Exception as e:
        logging.error(f"Dynamic Validation error: {e}")
        return False
