"""
SQLite database for tracking Instagram to WordPress post relationships
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PostTracker:
    """Track Instagram to WordPress post relationships using SQLite"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Store in project root/data directory
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "post_tracker.db"
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS instagram_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instagram_shortcode TEXT UNIQUE NOT NULL,
                    instagram_post_url TEXT,
                    instagram_username TEXT NOT NULL,
                    instagram_caption TEXT,
                    instagram_likes_count INTEGER DEFAULT 0,
                    instagram_comments_count INTEGER DEFAULT 0,
                    instagram_date_posted TEXT,
                    instagram_image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS wordpress_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wordpress_post_id INTEGER UNIQUE NOT NULL,
                    wordpress_title TEXT NOT NULL,
                    wordpress_status TEXT NOT NULL,
                    wordpress_permalink TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS post_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instagram_post_id INTEGER NOT NULL,
                    wordpress_post_id INTEGER NOT NULL,
                    import_method TEXT DEFAULT 'manual',
                    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (instagram_post_id) REFERENCES instagram_posts (id),
                    FOREIGN KEY (wordpress_post_id) REFERENCES wordpress_posts (id),
                    UNIQUE(instagram_post_id, wordpress_post_id)
                )
            ''')
            
            # Create indexes for faster lookups
            conn.execute('CREATE INDEX IF NOT EXISTS idx_instagram_shortcode ON instagram_posts (instagram_shortcode)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_instagram_username ON instagram_posts (instagram_username)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_wordpress_post_id ON wordpress_posts (wordpress_post_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_mapping_instagram ON post_mappings (instagram_post_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_mapping_wordpress ON post_mappings (wordpress_post_id)')
            
            conn.commit()
            logger.info(f"Initialized post tracker database: {self.db_path}")
    
    def add_instagram_post(self, post_data: Dict[str, Any]) -> int:
        """Add or update an Instagram post record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Try to insert, update if exists
            cursor.execute('''
                INSERT OR REPLACE INTO instagram_posts 
                (instagram_shortcode, instagram_post_url, instagram_username, 
                 instagram_caption, instagram_likes_count, instagram_comments_count,
                 instagram_date_posted, instagram_image_url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                post_data.get('shortcode'),
                post_data.get('post_url'),
                post_data.get('username'),
                post_data.get('caption', ''),
                post_data.get('likes_count', 0),
                post_data.get('comments_count', 0),
                post_data.get('date_posted'),
                post_data.get('image_url')
            ))
            
            # Get the ID of the inserted/updated record
            cursor.execute('SELECT id FROM instagram_posts WHERE instagram_shortcode = ?', 
                         (post_data.get('shortcode'),))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def add_wordpress_post(self, wordpress_id: int, title: str, status: str, permalink: str = None) -> int:
        """Add or update a WordPress post record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO wordpress_posts 
                (wordpress_post_id, wordpress_title, wordpress_status, wordpress_permalink, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (wordpress_id, title, status, permalink))
            
            cursor.execute('SELECT id FROM wordpress_posts WHERE wordpress_post_id = ?', (wordpress_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def create_mapping(self, instagram_shortcode: str, wordpress_post_id: int, import_method: str = 'manual') -> bool:
        """Create a mapping between Instagram and WordPress posts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get Instagram post internal ID
            cursor.execute('SELECT id FROM instagram_posts WHERE instagram_shortcode = ?', (instagram_shortcode,))
            instagram_result = cursor.fetchone()
            if not instagram_result:
                logger.error(f"Instagram post not found: {instagram_shortcode}")
                return False
            
            # Get WordPress post internal ID
            cursor.execute('SELECT id FROM wordpress_posts WHERE wordpress_post_id = ?', (wordpress_post_id,))
            wordpress_result = cursor.fetchone()
            if not wordpress_result:
                logger.error(f"WordPress post not found: {wordpress_post_id}")
                return False
            
            # Create mapping
            try:
                cursor.execute('''
                    INSERT INTO post_mappings (instagram_post_id, wordpress_post_id, import_method)
                    VALUES (?, ?, ?)
                ''', (instagram_result[0], wordpress_result[0], import_method))
                conn.commit()
                logger.info(f"Created mapping: {instagram_shortcode} -> WP {wordpress_post_id}")
                return True
            except sqlite3.IntegrityError:
                logger.warning(f"Mapping already exists: {instagram_shortcode} -> WP {wordpress_post_id}")
                return False
    
    def is_instagram_post_imported(self, shortcode: str) -> Optional[Dict[str, Any]]:
        """Check if an Instagram post has been imported to WordPress"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    i.instagram_shortcode,
                    i.instagram_username,
                    i.instagram_caption,
                    w.wordpress_post_id,
                    w.wordpress_title,
                    w.wordpress_status,
                    w.wordpress_permalink,
                    m.import_method,
                    m.import_date
                FROM instagram_posts i
                JOIN post_mappings m ON i.id = m.instagram_post_id
                JOIN wordpress_posts w ON m.wordpress_post_id = w.id
                WHERE i.instagram_shortcode = ?
            ''', (shortcode,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'instagram_shortcode': result[0],
                    'instagram_username': result[1],
                    'instagram_caption': result[2],
                    'wordpress_post_id': result[3],
                    'wordpress_title': result[4],
                    'wordpress_status': result[5],
                    'wordpress_permalink': result[6],
                    'import_method': result[7],
                    'import_date': result[8]
                }
            return None
    
    def get_imported_posts(self, username: str = None) -> List[Dict[str, Any]]:
        """Get all imported posts, optionally filtered by username"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    i.instagram_shortcode,
                    i.instagram_username,
                    i.instagram_caption,
                    w.wordpress_post_id,
                    w.wordpress_title,
                    w.wordpress_status,
                    w.wordpress_permalink,
                    m.import_method,
                    m.import_date
                FROM instagram_posts i
                JOIN post_mappings m ON i.id = m.instagram_post_id
                JOIN wordpress_posts w ON m.wordpress_post_id = w.id
            '''
            
            params = []
            if username:
                query += ' WHERE i.instagram_username = ?'
                params.append(username)
            
            query += ' ORDER BY m.import_date DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [{
                'instagram_shortcode': row[0],
                'instagram_username': row[1],
                'instagram_caption': row[2],
                'wordpress_post_id': row[3],
                'wordpress_title': row[4],
                'wordpress_status': row[5],
                'wordpress_permalink': row[6],
                'import_method': row[7],
                'import_date': row[8]
            } for row in results]
    
    def remove_mapping(self, shortcode: str) -> bool:
        """Remove a mapping (but keep the individual post records)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM post_mappings 
                WHERE instagram_post_id IN (
                    SELECT id FROM instagram_posts WHERE instagram_shortcode = ?
                )
            ''', (shortcode,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            
            if deleted:
                logger.info(f"Removed mapping for Instagram post: {shortcode}")
            
            return deleted
    
    def clear_all_mappings(self) -> int:
        """Clear all mappings (for cleanup)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM post_mappings')
            deleted_count = cursor.rowcount
            conn.commit()
            logger.info(f"Cleared {deleted_count} post mappings")
            return deleted_count
    
    def sync_with_wordpress(self, mcp_client) -> Dict[str, int]:
        """Sync SQLite database with current WordPress posts"""
        removed_mappings = 0
        updated_posts = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all current mappings
            cursor.execute('''
                SELECT m.id, w.wordpress_post_id, i.instagram_shortcode
                FROM post_mappings m
                JOIN wordpress_posts w ON m.wordpress_post_id = w.id
                JOIN instagram_posts i ON m.instagram_post_id = i.id
            ''')
            
            mappings = cursor.fetchall()
            
            for mapping_id, wp_post_id, shortcode in mappings:
                try:
                    # Check if WordPress post still exists
                    wp_posts = mcp_client.call_mcp_function('wp_get_posts', {
                        'include': [wp_post_id],
                        'post_status': 'any'
                    })
                    
                    if not wp_posts or len(wp_posts) == 0:
                        # Post was deleted, remove mapping
                        cursor.execute('DELETE FROM post_mappings WHERE id = ?', (mapping_id,))
                        removed_mappings += 1
                        logger.info(f"Removed mapping for deleted WP post {wp_post_id} (Instagram: {shortcode})")
                    else:
                        # Post exists, update its info
                        wp_post = wp_posts[0]
                        cursor.execute('''
                            UPDATE wordpress_posts 
                            SET wordpress_title = ?, wordpress_status = ?, wordpress_permalink = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE wordpress_post_id = ?
                        ''', (
                            wp_post.get('post_title', ''),
                            wp_post.get('post_status', ''),
                            wp_post.get('permalink', ''),
                            wp_post_id
                        ))
                        updated_posts += 1
                        
                except Exception as e:
                    logger.warning(f"Error checking WordPress post {wp_post_id}: {e}")
                    continue
            
            conn.commit()
            
        logger.info(f"Sync completed: {removed_mappings} mappings removed, {updated_posts} posts updated")
        
        return {
            'removed_mappings': removed_mappings,
            'updated_posts': updated_posts
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM instagram_posts')
            instagram_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM wordpress_posts')
            wordpress_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM post_mappings')
            mappings_count = cursor.fetchone()[0]
            
            return {
                'instagram_posts': instagram_count,
                'wordpress_posts': wordpress_count,
                'mappings': mappings_count
            }