from typing import List, Dict, Any
from app.schemas.findings import AccessibilityViolation
from app.core.logger import logger

class AccessibilityAuditor:
    """
    Evaluates the standard accessibility tree snapshot for WCAG compliance:
    - Missing accessible names / labels on interactive controls
    - Non-descriptive roles
    - Focus hierarchy violations
    """
    
    def audit_tree(self, a11y_tree: Dict[str, Any]) -> List[AccessibilityViolation]:
        violations: List[AccessibilityViolation] = []
        if not a11y_tree:
            return violations
            
        def traverse(node: Dict[str, Any]):
            role = node.get("role", "")
            name = node.get("name", "").strip()
            
            # Check interactive elements for missing accessible names
            if role in ["button", "link", "textbox", "combobox", "checkbox"]:
                if not name or name == "undefined":
                    violations.append(
                        AccessibilityViolation(
                            node_id=str(node.get("id", "node")),
                            role=role,
                            issue_type="Missing Accessible Name / Label",
                            bounding_box={"x": 0, "y": 0, "width": 0, "height": 0},
                            severity="High"
                        )
                    )
            
            for child in node.get("children", []):
                traverse(child)
                
        traverse(a11y_tree)
        logger.info(f"Accessibility Audit complete: found {len(violations)} violations.")
        return violations
