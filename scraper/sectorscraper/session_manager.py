"""
Session Manager for Scraping Progress
Manages scraping sessions and resume functionality using Supabase
"""

import uuid
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from database import DatabaseManager

class ScrapingSessionManager:
    """Manages scraping sessions and progress tracking"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.current_session_id: Optional[str] = None
        self.current_sector: int = 0
        self.total_sectors: int = 0
        
    def start_new_session(self, total_sectors: int, start_sector: int = 0) -> str:
        """Start a new scraping session"""
        try:
            self.current_session_id = str(uuid.uuid4())
            self.total_sectors = total_sectors
            self.current_sector = start_sector
            
            # Create session record in database
            session_data = {
                'session_id': self.current_session_id,
                'started_at': datetime.now().isoformat(),
                'total_restaurants': 0,
                'scraped_count': 0,
                'failed_count': 0,
                'is_completed': False,
                'last_updated': datetime.now().isoformat()
            }
            
            response = self.db_manager.supabase.table('scraping_progress').insert(session_data).execute()
            
            if response.data:
                self.logger.info(f"Started new scraping session: {self.current_session_id}")
                self.logger.info(f"Total sectors: {total_sectors}, Starting from sector: {start_sector}")
                return self.current_session_id
            else:
                self.logger.error("Failed to create session in database")
                return None
                
        except Exception as e:
            self.logger.error(f"Error starting new session: {e}")
            return None
    
    def resume_session(self, session_id: str) -> bool:
        """Resume an existing session"""
        try:
            # Get session data from database
            response = self.db_manager.supabase.table('scraping_progress').select('*').eq('session_id', session_id).execute()
            
            if not response.data:
                self.logger.error(f"Session {session_id} not found")
                return False
            
            session_data = response.data[0]
            
            if session_data['is_completed']:
                self.logger.warning(f"Session {session_id} is already completed")
                return False
            
            # Restore session state
            self.current_session_id = session_id
            self.total_sectors = 48  # Default to 48 sectors for Singapore
            self.current_sector = 0  # Will be determined by completed sectors
            
            self.logger.info(f"Resumed session {session_id}")
            self.logger.info(f"Scraped restaurants: {session_data.get('scraped_count', 0)}")
            self.logger.info(f"Failed restaurants: {session_data.get('failed_count', 0)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error resuming session {session_id}: {e}")
            return False
    
    def update_sector_progress(self, sector_num: int, status: str, restaurants_count: int = 0) -> bool:
        """Update progress for a specific sector"""
        try:
            if not self.current_session_id:
                self.logger.error("No active session to update")
                return False
            
            # Get current session data
            response = self.db_manager.supabase.table('scraping_progress').select('*').eq('session_id', self.current_session_id).execute()
            
            if not response.data:
                self.logger.error(f"Session {self.current_session_id} not found in database")
                return False
            
            session_data = response.data[0]
            current_scraped = session_data.get('scraped_count', 0)
            current_failed = session_data.get('failed_count', 0)
            
            # Update counts based on status
            if status == 'completed':
                new_scraped = current_scraped + restaurants_count
                new_failed = current_failed
            elif status == 'failed':
                new_scraped = current_scraped
                new_failed = current_failed + 1
            else:
                return True  # No change needed
            
            # Update database
            update_data = {
                'scraped_count': new_scraped,
                'failed_count': new_failed,
                'last_updated': datetime.now().isoformat()
            }
            
            response = self.db_manager.supabase.table('scraping_progress').update(update_data).eq('session_id', self.current_session_id).execute()
            
            if response.data:
                self.logger.info(f"Updated sector {sector_num} status: {status} ({restaurants_count} restaurants)")
                return True
            else:
                self.logger.error(f"Failed to update sector {sector_num} progress")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating sector {sector_num} progress: {e}")
            return False
    
    def get_session_progress(self) -> Dict:
        """Get current session progress"""
        try:
            if not self.current_session_id:
                return {}
            
            response = self.db_manager.supabase.table('scraping_progress').select('*').eq('session_id', self.current_session_id).execute()
            
            if not response.data:
                return {}
            
            session_data = response.data[0]
            
            return {
                'session_id': self.current_session_id,
                'total_sectors': self.total_sectors,
                'current_sector': self.current_sector,
                'completed_sectors': 0,  # Not tracked in current schema
                'failed_sectors': 0,  # Not tracked in current schema
                'scraped_count': session_data.get('scraped_count', 0),
                'failed_count': session_data.get('failed_count', 0),
                'is_completed': session_data.get('is_completed', False),
                'started_at': session_data.get('started_at'),
                'last_updated': session_data.get('last_updated')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting session progress: {e}")
            return {}
    
    def complete_session(self) -> bool:
        """Mark the current session as completed"""
        try:
            if not self.current_session_id:
                self.logger.error("No active session to complete")
                return False
            
            update_data = {
                'is_completed': True,
                'last_updated': datetime.now().isoformat()
            }
            
            response = self.db_manager.supabase.table('scraping_progress').update(update_data).eq('session_id', self.current_session_id).execute()
            
            if response.data:
                self.logger.info(f"Completed session {self.current_session_id}")
                return True
            else:
                self.logger.error(f"Failed to complete session {self.current_session_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error completing session: {e}")
            return False
    
    def get_available_sessions(self) -> List[Dict]:
        """Get list of available sessions"""
        try:
            response = self.db_manager.supabase.table('scraping_progress').select('*').order('started_at', desc=True).execute()
            
            if response.data:
                sessions = []
                for session in response.data:
                    sessions.append({
                        'session_id': session['session_id'],
                        'started_at': session['started_at'],
                        'total_sectors': 48,  # Default for Singapore
                        'current_sector': 0,  # Not tracked in current schema
                        'completed_sectors': 0,  # Not tracked in current schema
                        'failed_sectors': 0,  # Not tracked in current schema
                        'scraped_count': session.get('scraped_count', 0),
                        'failed_count': session.get('failed_count', 0),
                        'is_completed': session.get('is_completed', False),
                        'last_updated': session.get('last_updated')
                    })
                return sessions
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting available sessions: {e}")
            return []
    
    def get_next_sector_to_process(self) -> int:
        """Get the next sector number to process"""
        try:
            if not self.current_session_id:
                return 0
            
            response = self.db_manager.supabase.table('scraping_progress').select('*').eq('session_id', self.current_session_id).execute()
            
            if not response.data:
                return 0
            
            session_data = response.data[0]
            scraped_count = session_data.get('scraped_count', 0)
            
            # Estimate next sector based on restaurants scraped
            # Assuming ~81 restaurants per sector, estimate which sector to start from
            estimated_sector = (scraped_count // 81) + 1
            
            return min(estimated_sector, self.total_sectors)
            
        except Exception as e:
            self.logger.error(f"Error getting next sector: {e}")
            return 0