# Medication Service for database queries and medication knowledge
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.medication import Medication
import re


class MedicationService:
    """Service for medication data operations"""
    
    def search_medications(
        self, 
        db: Session, 
        query: str, 
        skip: int = 0, 
        limit: int = 50,
        include_discontinued: bool = False
    ) -> List[Medication]:
        """
        Search medications by name or uses
        
        Args:
            db: Database session
            query: Search query
            skip: Number of results to skip
            limit: Maximum results to return
            include_discontinued: Whether to include discontinued medications
        
        Returns:
            List of matching medications
        """
        search_filter = or_(
            func.lower(Medication.name).contains(query.lower()),
            func.lower(Medication.uses).contains(query.lower())
        )
        
        if not include_discontinued:
            search_filter = search_filter & (Medication.discontinued == False)
        
        medications = db.query(Medication).filter(search_filter).offset(skip).limit(limit).all()
        return medications
    
    def get_medication_by_name(self, db: Session, name: str) -> Optional[Medication]:
        """
        Get medication by exact name (case-insensitive)
        
        Args:
            db: Database session
            name: Medication name
        
        Returns:
            Medication if found, None otherwise
        """
        return db.query(Medication).filter(
            func.lower(Medication.name) == name.lower()
        ).first()
    
    def get_medication_by_id(self, db: Session, medication_id: int) -> Optional[Medication]:
        """Get medication by ID"""
        return db.query(Medication).filter(Medication.id == medication_id).first()
    
    def list_medications(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        discontinued_only: bool = False
    ) -> tuple[List[Medication], int]:
        """
        List medications with pagination
        
        Returns:
            Tuple of (medications list, total count)
        """
        query = db.query(Medication)
        
        if discontinued_only:
            query = query.filter(Medication.discontinued == True)
        
        total = query.count()
        medications = query.offset(skip).limit(limit).all()
        
        return medications, total
    
    def check_discontinued(self, db: Session, name: str) -> bool:
        """
        Check if medication is discontinued
        
        Args:
            db: Database session
            name: Medication name
        
        Returns:
            True if discontinued, False otherwise
        """
        medication = self.get_medication_by_name(db, name)
        return medication.discontinued if medication else False
    
    def get_medication_context(self, db: Session, text: str) -> List[Dict]:
        """
        Extract medication mentions from text and return their details
        
        Args:
            db: Database session
            text: Text to analyze (e.g., medical note)
        
        Returns:
            List of dictionaries with medication information
        """
        # Get all medications from database
        all_medications = db.query(Medication).all()
        
        found_medications = []
        text_lower = text.lower()
        
        for med in all_medications:
            # Check if medication name appears in text
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(med.name.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_medications.append({
                    'name': med.name,
                    'uses': med.uses,
                    'side_effects': med.side_effects,
                    'discontinued': med.discontinued,
                    'discontinuation_reason': med.discontinuation_reason,
                    'warning': 'DISCONTINUED' if med.discontinued else None
                })
        
        return found_medications
    
    def create_medication(self, db: Session, medication_data: Dict) -> Medication:
        """
        Create a new medication
        
        Args:
            db: Database session
            medication_data: Dictionary with medication fields
        
        Returns:
            Created Medication object
        """
        medication = Medication(**medication_data)
        db.add(medication)
        db.commit()
        db.refresh(medication)
        return medication
    
    def update_medication(self, db: Session, medication_id: int, update_data: Dict) -> Optional[Medication]:
        """
        Update an existing medication
        
        Args:
            db: Database session
            medication_id: ID of medication to update
            update_data: Dictionary with fields to update
        
        Returns:
            Updated Medication object or None
        """
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        
        if not medication:
            return None
        
        # Update only provided fields
        for field, value in update_data.items():
            if hasattr(medication, field) and field != 'id':
                setattr(medication, field, value)
        
        db.commit()
        db.refresh(medication)
        return medication
    
    def bulk_create_medications(self, db: Session, medications_data: List[Dict], update_existing: bool = True) -> Dict[str, int]:
        """
        Create or update multiple medications from a list of dictionaries
        
        Args:
            db: Database session
            medications_data: List of dicts with medication info
            update_existing: If True, updates existing medications with new data
        
        Returns:
            Dictionary with counts: {'created': X, 'updated': Y, 'skipped': Z}
        """
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for med_data in medications_data:
            # Check if medication already exists
            existing = self.get_medication_by_name(db, med_data['name'])
            
            if existing and update_existing:
                # Check if any field has changed
                has_changes = False
                for field, new_value in med_data.items():
                    if field in ['name', 'id']:
                        continue
                    old_value = getattr(existing, field, None)
                    # Compare, treating None and empty string as equivalent
                    if (new_value or old_value) and new_value != old_value:
                        has_changes = True
                        break
                
                if has_changes:
                    # Update existing medication
                    update_data = {k: v for k, v in med_data.items() if k not in ['name', 'id']}
                    if self.update_medication(db, existing.id, update_data):
                        updated_count += 1
                else:
                    skipped_count += 1
            elif existing:
                skipped_count += 1
            else:
                # Create new medication
                medication = self.create_medication(db, med_data)
                if medication:
                    created_count += 1
        
        return {
            'created': created_count,
            'updated': updated_count,
            'skipped': skipped_count
        }


# Create singleton instance
medication_service = MedicationService()
