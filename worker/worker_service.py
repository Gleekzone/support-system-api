# services/worker_service.py
import json, aioboto3
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from common.models.ticket import TicketImportJob, Ticket
from common.logger import logger


class WorkerService:
    def __init__(self, db: Session = None):
        self.db = db
        self.s3_session = aioboto3.Session()
    
    def _parse_s3_url(self, url: str):
        """Convert s3://bucket/key into bucket and key"""
        url = url.replace("s3://", "")
        bucket, key = url.split("/", 1)
        return bucket, key

    async def process_job(self, job: TicketImportJob):
        """Process a ticket import job from S3."""
        logger.info(f"Start processing job_id {job.id}")
        bucket, key = self._parse_s3_url(job.s3_url)

        try:
            async with self.s3_session.client("s3") as s3_client:
                logger.info(f"Downloading file from S3: {job.s3_url}")
                obj = await s3_client.get_object(Bucket=bucket, Key=key)
                content = await obj["Body"].read()
                tickets_list = json.loads(content)

                for row in tickets_list:
                    ticket = Ticket(
                        reporter_name=row["reporter_name"],
                        reporter_email=row["reporter_email"],
                        description=row["description"],
                        assigned_to_id=row["assigned_to_id"] if "assigned_to_id" in row else None,
                    )
                    self.db.add(ticket)
                await self.db.commit()
                logger.info(f"Inserted {len(tickets_list)} tickets for job_id {job.id}")

            job.status = "COMPLETED"
            job.processed_at = func.now()
            self.db.add(job)
            await self.db.commit()
            logger.info(f"Job {job.id} completed successfully")
        except Exception as e:
            logger.error(f"Job {job.id} failed: {e}", exc_info=True)
            job.status = "FAILED"
            self.db.add(job)
            await self.db.commit()
            raise e
        finally:
            await self.db.close()
