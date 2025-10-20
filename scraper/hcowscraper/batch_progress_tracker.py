#!/usr/bin/env python3
"""
Batch Progress Tracker for HappyCow Scraper
Handles batch processing and progress checkpointing
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from database import DatabaseManager
from models import Restaurant

class BatchProgressTracker:
    """Track scraping progress with batch processing and resume capability"""
    
    def __init__(self, db_manager: DatabaseManager, batch_size: int = 20):
        self.db_manager = db_manager
        self.batch_size = batch_size
        self.session_id = str(uuid.uuid4())
        self.logger = logging.getLogger(__name__)
        
        # Initialize progress tracking
        self.total_restaurants = 0
        self.processed_restaurants = 0
        self.current_batch = 0
        self.total_batches = 0
        self.is_completed = False
        self.error_message = None
        
    def start_scraping_session(self, total_restaurants: int) -> bool:
        """Start a new scraping session"""
        try:
            self.total_restaurants = total_restaurants
            self.total_batches = (total_restaurants + self.batch_size - 1) // self.batch_size
            self.current_batch = 0
            self.processed_restaurants = 0
            self.is_completed = False
            self.error_message = None
            
            # Create initial progress record
            if self.db_manager and self.db_manager.supabase:
                progress_data = {
                    'session_id': self.session_id,
                    'total_restaurants': self.total_restaurants,
                    'processed_restaurants': 0,
                    'current_batch': 0,
                    'total_batches': self.total_batches,
                    'batch_size': self.batch_size,
                    'is_completed': False,
                    'resume_from_batch': 0
                }
                
                result = self.db_manager.supabase.table('scraping_progress').insert(progress_data).execute()
                if result.data:
                    self.logger.info(f"Started scraping session {self.session_id}: {self.total_restaurants} restaurants in {self.total_batches} batches")
                    return True
                else:
                    self.logger.error("Failed to create progress record")
                    return False
            else:
                self.logger.warning("No database connection for progress tracking")
                return True
                
        except Exception as e:
            self.logger.error(f"Error starting scraping session: {e}")
            return False
    
    def resume_scraping_session(self, session_id: str) -> bool:
        """Resume an existing scraping session"""
        try:
            if not self.db_manager or not self.db_manager.supabase:
                self.logger.warning("No database connection for progress tracking")
                return False
            
            # Get latest progress for this session
            result = self.db_manager.supabase.rpc('get_latest_progress', {'session_id_param': session_id}).execute()
            
            if result.data and len(result.data) > 0:
                progress = result.data[0]
                self.session_id = session_id
                self.total_restaurants = progress['total_restaurants']
                self.processed_restaurants = progress['processed_restaurants']
                self.current_batch = progress['current_batch']
                self.total_batches = progress['total_batches']
                self.batch_size = progress['batch_size']
                self.is_completed = progress['is_completed']
                self.error_message = progress['error_message']
                
                self.logger.info(f"Resumed scraping session {session_id}: {self.processed_restaurants}/{self.total_restaurants} processed")
                return True
            else:
                self.logger.warning(f"No progress found for session {session_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error resuming scraping session: {e}")
            return False
    
    def process_batch(self, restaurants: List[Restaurant]) -> Tuple[bool, int, int]:
        """Process a batch of restaurants and update progress"""
        try:
            if not restaurants:
                return True, 0, 0
            
            # Insert batch into database
            success, inserted_count, skipped_count = self.db_manager.insert_restaurants(restaurants)
            
            if success:
                # Update progress
                self.processed_restaurants += inserted_count
                self.current_batch += 1
                
                # Update progress in database
                if self.db_manager and self.db_manager.supabase:
                    self.db_manager.supabase.rpc('update_scraping_progress', {
                        'session_id_param': self.session_id,
                        'processed_count': self.processed_restaurants,
                        'current_batch_param': self.current_batch,
                        'is_completed_param': False,
                        'error_msg': None
                    }).execute()
                
                self.logger.info(f"Batch {self.current_batch}/{self.total_batches} completed: {inserted_count} inserted, {skipped_count} skipped")
                return True, inserted_count, skipped_count
            else:
                self.logger.error(f"Failed to insert batch {self.current_batch + 1}")
                return False, 0, 0
                
        except Exception as e:
            self.logger.error(f"Error processing batch: {e}")
            self._record_error(str(e))
            return False, 0, 0
    
    def complete_scraping_session(self) -> bool:
        """Mark scraping session as completed"""
        try:
            self.is_completed = True
            
            if self.db_manager and self.db_manager.supabase:
                self.db_manager.supabase.rpc('update_scraping_progress', {
                    'session_id_param': self.session_id,
                    'processed_count': self.processed_restaurants,
                    'current_batch_param': self.current_batch,
                    'is_completed_param': True,
                    'error_msg': None
                }).execute()
            
            self.logger.info(f"Scraping session {self.session_id} completed: {self.processed_restaurants}/{self.total_restaurants} restaurants processed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error completing scraping session: {e}")
            return False
    
    def _record_error(self, error_message: str):
        """Record an error in the progress tracking"""
        try:
            self.error_message = error_message
            
            if self.db_manager and self.db_manager.supabase:
                self.db_manager.supabase.rpc('update_scraping_progress', {
                    'session_id_param': self.session_id,
                    'processed_count': self.processed_restaurants,
                    'current_batch_param': self.current_batch,
                    'is_completed_param': False,
                    'error_msg': error_message
                }).execute()
                
        except Exception as e:
            self.logger.error(f"Error recording error: {e}")
    
    def get_progress_summary(self) -> Dict:
        """Get current progress summary"""
        return {
            'session_id': self.session_id,
            'total_restaurants': self.total_restaurants,
            'processed_restaurants': self.processed_restaurants,
            'current_batch': self.current_batch,
            'total_batches': self.total_batches,
            'batch_size': self.batch_size,
            'is_completed': self.is_completed,
            'progress_percentage': (self.processed_restaurants / self.total_restaurants * 100) if self.total_restaurants > 0 else 0,
            'error_message': self.error_message
        }
    
    def get_available_sessions(self) -> List[Dict]:
        """Get list of available scraping sessions"""
        try:
            if not self.db_manager or not self.db_manager.supabase:
                return []
            
            result = self.db_manager.supabase.table('scraping_progress').select('*').order('started_at', desc=True).execute()
            return result.data if result.data else []
            
        except Exception as e:
            self.logger.error(f"Error getting available sessions: {e}")
            return []
    
    def cleanup_old_sessions(self, days_old: int = 7) -> bool:
        """Clean up old scraping sessions"""
        try:
            if not self.db_manager or not self.db_manager.supabase:
                return False
            
            # Delete sessions older than specified days
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
            
            result = self.db_manager.supabase.table('scraping_progress').delete().lt('started_at', cutoff_date.isoformat()).execute()
            
            self.logger.info(f"Cleaned up {len(result.data) if result.data else 0} old sessions")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old sessions: {e}")
            return False
