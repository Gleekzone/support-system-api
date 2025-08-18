import json
import asyncio
from common.db import SessionLocal
from common.models.ticket import TicketImportJob
from worker.worker_service import WorkerService
from common.logger import logger


def lambda_handler(event, context):
    """ Lambda handler to process ticket import jobs from SQS."""
    session = SessionLocal()
    worker_service = WorkerService(db_session=session)

    try:
        for record in event.get("Records", []):
            try:
                msg = json.loads(record["body"])
                job_id = msg["job_id"]
                job = session.get(TicketImportJob, job_id)
                if job is None:
                    logger.warning(f"Job {job_id} not found")
                    continue

                # Execute the job processing asynchronously
                asyncio.run(worker_service.process_job(job))

            except Exception as job_err:
                logger.error(f"Error processing job {msg.get('job_id')}: {job_err}", exc_info=True)

    except Exception as e:
        logger.critical(f"Unexpected error in lambda_handler: {e}", exc_info=True)
        raise 

    finally:
        session.close()
