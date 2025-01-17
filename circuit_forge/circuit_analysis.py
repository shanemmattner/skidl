import os
import json
import io
import sqlite3
import hashlib
from datetime import datetime
from contextlib import redirect_stdout
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging
import anthropic
from anthropic._exceptions import APIConnectionError, APIError

# Configure logging with a structured approach
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger('circuit_analysis')
debug_logger = logging.getLogger('circuit_analysis.debug')

class ValidationSeverity(Enum):
    """Severity levels for validation rules."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def analyze_circuit(self, report: str, circuit_json: str) -> Dict:
        """Analyze circuit using the LLM provider."""
        pass

class ClaudeProvider(LLMProvider):
    """Anthropic Claude LLM provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize with API key and model."""
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Client(api_key=api_key)
        logger.info(f"Initialized Claude provider with model: {model}")
        
    def analyze_circuit(self, report: str, circuit_json: str) -> Dict:
        """Analyze circuit using Claude."""
        try:
            debug_logger.info("Starting Claude circuit analysis")
            query = self._generate_query(report, circuit_json)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system="You are an expert electronics engineer analyzing circuit designs. Focus on practical improvements for reliability and safety.",
                messages=[{
                    "role": "user",
                    "content": query
                }]
            )
            
            result = {
                "query": query,
                "response": response.content[0].text,
                "timestamp": datetime.now().isoformat()
            }
            
            debug_logger.info("Claude analysis completed successfully")
            return result
            
        except APIConnectionError as e:
            logger.error(f"Connection error with Anthropic API: {str(e)}")
            raise
        except APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Claude analysis: {str(e)}", exc_info=True)
            raise
            
    def _generate_query(self, circuit_report: str, circuit_json: str) -> str:
        """Generate analysis query for Claude."""
        debug_logger.info("Generating Claude query")
        query = f"""
    Please provide a detailed electronic circuit analysis for the following design.

    ## Circuit Report
    {circuit_report}

    ## Circuit Definition
    ```json
    {circuit_json}
    ```

    [Rest of the detailed query format...]"""
        
        debug_logger.debug(f"Generated query of {len(query)} characters")
        return query

@dataclass
class ValidationRule:
    """Represents a single validation rule with configuration."""
    name: str
    description: str
    category: str
    severity: ValidationSeverity
    check_function: callable
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Result from a validation check."""
    rule_name: str
    message: str
    severity: ValidationSeverity
    details: Optional[Dict[str, Any]] = None

@dataclass 
class CircuitHash:
    """Represents a circuit's hash state."""
    full_hash: str
    component_hashes: Dict[str, str]
    net_hashes: Dict[str, str]
    timestamp: datetime

@dataclass
class AnalysisConfig:
    """Configuration for circuit analysis."""
    # Analysis flags
    check_power: bool = True
    check_connections: bool = True
    check_components: bool = True
    check_standards: bool = True
    check_safety: bool = True
    verbose: bool = False
    
    # LLM configuration
    llm_provider: str = "claude"  # "claude", "openai", or "gemini"
    llm_model: str = "claude-3-5-haiku-20241022"
    use_cache: bool = True
    
    # Validation configuration
    validation_severity: ValidationSeverity = ValidationSeverity.WARNING
    validation_categories: List[str] = field(default_factory=lambda: ["power", "signals", "components"])
    custom_validation_rules: Dict[str, ValidationRule] = field(default_factory=dict)
    
    # Cache configuration
    cache_dir: str = ".circuit_forge_cache"
    force_reanalysis: bool = False

class ValidationManager:
    """Manages validation rules and their execution."""
    
    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default validation rules with reasonable defaults."""
        # Power validation rules
        self.add_rule(
            ValidationRule(
                name="power_nets_present",
                description="Check for presence of power nets",
                category="power",
                severity=ValidationSeverity.ERROR,
                check_function=self._check_power_nets,
                parameters={"required_nets": ["VDD", "GND"]}
            )
        )
        
        self.add_rule(
            ValidationRule(
                name="decoupling_caps",
                description="Check for proper decoupling capacitors",
                category="power",
                severity=ValidationSeverity.WARNING,
                check_function=self._check_decoupling,
                parameters={"min_caps_per_ic": 1}
            )
        )
        
        # Signal integrity rules
        self.add_rule(
            ValidationRule(
                name="floating_inputs",
                description="Check for floating input pins",
                category="signals",
                severity=ValidationSeverity.ERROR,
                check_function=self._check_floating_inputs
            )
        )
        
        # Component rules
        self.add_rule(
            ValidationRule(
                name="duplicate_refs",
                description="Check for duplicate reference designators",
                category="components",
                severity=ValidationSeverity.ERROR,
                check_function=self._check_duplicate_refs
            )
        )
    
    def add_rule(self, rule: ValidationRule):
        """Add a new validation rule."""
        self.rules[rule.name] = rule
        logger.info(f"Added validation rule: {rule.name}")
    
    def disable_rule(self, rule_name: str):
        """Disable a validation rule."""
        if rule_name in self.rules:
            self.rules[rule_name].enabled = False
            logger.info(f"Disabled validation rule: {rule_name}")
    
    def enable_rule(self, rule_name: str):
        """Enable a validation rule."""
        if rule_name in self.rules:
            self.rules[rule_name].enabled = True
            logger.info(f"Enabled validation rule: {rule_name}")
    
    def update_rule_severity(self, rule_name: str, severity: ValidationSeverity):
        """Update the severity level of a rule."""
        if rule_name in self.rules:
            self.rules[rule_name].severity = severity
            logger.info(f"Updated severity for {rule_name} to {severity.value}")
    
    def update_rule_parameters(self, rule_name: str, parameters: Dict[str, Any]):
        """Update the parameters for a rule."""
        if rule_name in self.rules:
            self.rules[rule_name].parameters.update(parameters)
            logger.info(f"Updated parameters for {rule_name}")
    
    def validate_circuit(self, circuit: 'Circuit', config: AnalysisConfig) -> List[ValidationResult]:
        """Run all enabled validation rules on a circuit."""
        results = []
        
        for rule in self.rules.values():
            if rule.enabled and rule.category in config.validation_categories:
                if rule.severity.value >= config.validation_severity.value:
                    try:
                        rule_results = rule.check_function(circuit, rule.parameters)
                        if isinstance(rule_results, list):
                            results.extend([
                                ValidationResult(
                                    rule_name=rule.name,
                                    message=msg,
                                    severity=rule.severity
                                ) for msg in rule_results
                            ])
                        elif rule_results:  # Single result
                            results.append(ValidationResult(
                                rule_name=rule.name,
                                message=rule_results,
                                severity=rule.severity
                            ))
                    except Exception as e:
                        logger.error(f"Error running validation rule {rule.name}: {str(e)}")
                        results.append(ValidationResult(
                            rule_name=rule.name,
                            message=f"Validation error: {str(e)}",
                            severity=ValidationSeverity.ERROR
                        ))
        
        return results

    # Default validation check implementations
    def _check_power_nets(self, circuit: 'Circuit', params: Dict[str, Any]) -> List[str]:
        required_nets = params.get('required_nets', ['VDD', 'GND'])
        errors = []
        
        circuit_nets = [net.name for net in circuit.get_nets()]
        for net_name in required_nets:
            if not any(net_name in n for n in circuit_nets):
                errors.append(f"Required power net {net_name} not found")
                
        return errors
    
    def _check_decoupling(self, circuit: 'Circuit', params: Dict[str, Any]) -> List[str]:
        min_caps = params.get('min_caps_per_ic', 1)
        warnings = []
        
        for component in circuit.components:
            if component.name.startswith('U') or component.name.startswith('IC'):
                caps = [c for c in circuit.components 
                       if c.name == 'C' and 
                       any(p.net == pin.net for p in c.pins.values() 
                           for pin in component.pins.values())]
                if len(caps) < min_caps:
                    warnings.append(
                        f"Insufficient decoupling capacitors for {component.ref}. "
                        f"Found {len(caps)}, need {min_caps}"
                    )
        
        return warnings
    
    def _check_floating_inputs(self, circuit: 'Circuit', params: Dict[str, Any]) -> List[str]:
        errors = []
        
        for component in circuit.components:
            for pin in component.pins.values():
                if (pin.electrical_type == 'input' and 
                    not pin.net and 
                    not pin.name.startswith('NC')):
                    errors.append(f"Floating input pin: {component.ref}.{pin.name}")
        
        return errors
    
    def _check_duplicate_refs(self, circuit: 'Circuit', params: Dict[str, Any]) -> List[str]:
        errors = []
        refs = [c.ref for c in circuit.components]
        seen = set()
        
        for ref in refs:
            if ref in seen:
                errors.append(f"Duplicate reference designator: {ref}")
            seen.add(ref)
            
        return errors


class CircuitChangeDetector:
    """Tracks changes in circuit design and manages analysis cache."""
    
    def __init__(self, cache_dir: str = ".circuit_forge_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.db_path = os.path.join(cache_dir, "analysis_cache.db")
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database for caching."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS circuit_cache (
                    circuit_name TEXT,
                    hash TEXT PRIMARY KEY,
                    analysis_data TEXT,
                    timestamp DATETIME
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS component_cache (
                    circuit_name TEXT,
                    component_ref TEXT,
                    hash TEXT,
                    analysis_data TEXT,
                    timestamp DATETIME,
                    PRIMARY KEY (circuit_name, component_ref, hash)
                )
            """)
    
    def compute_circuit_hash(self, circuit: 'Circuit') -> CircuitHash:
        """Compute hash for entire circuit and individual components."""
        component_hashes = {}
        for component in circuit.components:
            comp_dict = {
                'ref': component.ref,
                'name': component.name,
                'library': component.library,
                'pins': {num: pin.name for num, pin in component.pins.items()},
                'parameters': component.parameters
            }
            comp_hash = hashlib.sha256(
                json.dumps(comp_dict, sort_keys=True).encode()
            ).hexdigest()
            component_hashes[component.ref] = comp_hash
            
        net_hashes = {}
        for net_name, net in circuit.nets.items():
            net_dict = {
                'name': net_name,
                'connections': sorted([
                    f"{pin.parent.ref}.{pin.name}" for pin in net.pins
                ])
            }
            net_hash = hashlib.sha256(
                json.dumps(net_dict, sort_keys=True).encode()
            ).hexdigest()
            net_hashes[net_name] = net_hash
            
        full_dict = {
            'components': component_hashes,
            'nets': net_hashes
        }
        full_hash = hashlib.sha256(
            json.dumps(full_dict, sort_keys=True).encode()
        ).hexdigest()
        
        return CircuitHash(
            full_hash=full_hash,
            component_hashes=component_hashes,
            net_hashes=net_hashes,
            timestamp=datetime.now()
        )
    
    def _load_cached_hash(self, circuit_name: str) -> Optional[CircuitHash]:
        """Load the previous circuit hash from cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT hash, analysis_data, timestamp 
                FROM circuit_cache 
                WHERE circuit_name = ?
                ORDER BY timestamp DESC 
                LIMIT 1
                """,
                (circuit_name,)
            )
            row = cursor.fetchone()
            
            if row:
                analysis_data = json.loads(row[1])
                return CircuitHash(
                    full_hash=row[0],
                    component_hashes=analysis_data.get('component_hashes', {}),
                    net_hashes=analysis_data.get('net_hashes', {}),
                    timestamp=datetime.fromisoformat(row[2])
                )
        return None
    
    def detect_changes(self, 
                      circuit: 'Circuit',
                      prev_hash: Optional[CircuitHash] = None) -> Dict[str, Set[str]]:
        """Detect which parts of the circuit have changed."""
        current_hash = self.compute_circuit_hash(circuit)
        
        if prev_hash is None:
            prev_hash = self._load_cached_hash(circuit.metadata.name)
            
        if prev_hash is None:
            return {
                'new_components': set(current_hash.component_hashes.keys()),
                'modified_components': set(),
                'deleted_components': set(),
                'new_nets': set(current_hash.net_hashes.keys()),
                'modified_nets': set(),
                'deleted_nets': set()
            }
            
        changes = {
            'new_components': set(),
            'modified_components': set(),
            'deleted_components': set(),
            'new_nets': set(),
            'modified_nets': set(),
            'deleted_nets': set()
        }
        
        # Detect component changes
        current_components = set(current_hash.component_hashes.keys())
        prev_components = set(prev_hash.component_hashes.keys())
        
        changes['new_components'] = current_components - prev_components
        changes['deleted_components'] = prev_components - current_components
        
        for ref in current_components & prev_components:
            if current_hash.component_hashes[ref] != prev_hash.component_hashes[ref]:
                changes['modified_components'].add(ref)
                
        # Detect net changes
        current_nets = set(current_hash.net_hashes.keys())
        prev_nets = set(prev_hash.net_hashes.keys())
        
        changes['new_nets'] = current_nets - prev_nets
        changes['deleted_nets'] = prev_nets - current_nets
        
        for net in current_nets & prev_nets:
            if current_hash.net_hashes[net] != prev_hash.net_hashes[net]:
                changes['modified_nets'].add(net)
                
        return {
            'new_components': list(changes['new_components']),
            'modified_components': list(changes['modified_components']),
            'deleted_components': list(changes['deleted_components']),
            'new_nets': list(changes['new_nets']),
            'modified_nets': list(changes['modified_nets']),
            'deleted_nets': list(changes['deleted_nets'])
        }    
    def _serialize_for_cache(self, data: Dict) -> Dict:
        """Convert data structures to JSON serializable formats."""
        def convert_value(v):
            if isinstance(v, set):
                return list(v)
            if isinstance(v, datetime):
                return v.isoformat()
            if hasattr(v, '__dict__'):
                return v.__dict__
            return v

        return {
            k: convert_value(v) if isinstance(v, (set, datetime)) else v
            for k, v in data.items()
        }
    
    def cache_analysis(self, circuit: 'Circuit', analysis_results: Dict, component_results: Dict[str, Dict] = None):
        """Cache analysis results for the circuit and components."""
        circuit_hash = self.compute_circuit_hash(circuit)
        
        # Serialize the data before storing
        serialized_results = self._serialize_for_cache(analysis_results)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO circuit_cache 
                (circuit_name, hash, analysis_data, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (
                    circuit.metadata.name,
                    circuit_hash.full_hash,
                    json.dumps(serialized_results),
                    circuit_hash.timestamp.isoformat()
                )
            )
            
            if component_results:
                for ref, results in component_results.items():
                    if ref in circuit_hash.component_hashes:
                        serialized_comp_results = self._serialize_for_cache(results)
                        conn.execute(
                            """
                            INSERT OR REPLACE INTO component_cache
                            (circuit_name, component_ref, hash, analysis_data, timestamp)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                circuit.metadata.name,
                                ref,
                                circuit_hash.component_hashes[ref],
                                json.dumps(serialized_comp_results),
                                circuit_hash.timestamp.isoformat()
                            )
                        )

    def get_cached_analysis(self, 
                          circuit: 'Circuit',
                          component_ref: Optional[str] = None) -> Optional[Dict]:
        """Retrieve cached analysis results."""
        circuit_hash = self.compute_circuit_hash(circuit)
        
        with sqlite3.connect(self.db_path) as conn:
            if component_ref:
                if component_ref in circuit_hash.component_hashes:
                    cursor = conn.execute(
                        """
                        SELECT analysis_data FROM component_cache
                        WHERE circuit_name = ? AND component_ref = ? AND hash = ?
                        """,
                        (
                            circuit.metadata.name,
                            component_ref,
                            circuit_hash.component_hashes[component_ref]
                        )
                    )
                    row = cursor.fetchone()
                    if row:
                        return json.loads(row[0])
            else:
                cursor = conn.execute(
                    """
                    SELECT analysis_data FROM circuit_cache
                    WHERE circuit_name = ? AND hash = ?
                    """,
                    (circuit.metadata.name, circuit_hash.full_hash)
                )
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
        return None
    
class CircuitAnalyzer:
    """Main circuit analysis class that coordinates validation, caching, and LLM analysis."""

    def __init__(self, api_key: Optional[str] = None, config: Optional[AnalysisConfig] = None):
        """Initialize the circuit analyzer with all necessary components."""
        self.config = config or AnalysisConfig()
        self.output_dir = 'analysis_output'
        os.makedirs(self.output_dir, exist_ok=True)

        # Set up logging
        self._setup_logging()
        
        # Initialize components
        self.validator = ValidationManager()
        self.change_detector = CircuitChangeDetector(self.config.cache_dir)
        
        # Initialize LLM provider
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.warning("No API key found - LLM analysis will be disabled")
            self.llm = None
        else:
            self.llm = self._initialize_llm_provider()

    def _setup_logging(self):
        """Configure logging handlers."""
        debug_file = os.path.join(self.output_dir, 'debug.log')
        file_handler = logging.FileHandler(debug_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        debug_logger.addHandler(file_handler)
        debug_logger.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    def _initialize_llm_provider(self) -> Optional[LLMProvider]:
        """Initialize the appropriate LLM provider based on configuration."""
        try:
            if self.config.llm_provider == "claude":
                return ClaudeProvider(self.api_key, model=self.config.llm_model)
            else:
                logger.warning(f"Unsupported LLM provider: {self.config.llm_provider}")
                return None
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {str(e)}")
            return None

    def analyze_circuit(self, circuit: 'Circuit', config: Optional[AnalysisConfig] = None) -> Dict:
        """Perform comprehensive circuit analysis with caching and selective reanalysis."""
        if config:
            self.config = config

        logger.info("Starting circuit analysis")
        debug_logger.debug(f"Analysis config: {self.config}")

        try:
            # Check for cached analysis if enabled
            if self.config.use_cache and not self.config.force_reanalysis:
                cached_analysis = self.change_detector.get_cached_analysis(circuit)
                if cached_analysis:
                    changes = self.change_detector.detect_changes(circuit)
                    if not any(changes.values()):  # No changes detected
                        logger.info("Using cached analysis - no circuit changes detected")
                        return cached_analysis

            results = {
                'basic_analysis': self._perform_basic_analysis(circuit),
                'validation_results': self.validator.validate_circuit(circuit, self.config),
                'llm_analysis': None,
                'changes': None,
                'errors': [],
                'warnings': []
            }

            # Add change detection results if using cache
            if self.config.use_cache:
                changes = self.change_detector.detect_changes(circuit)
                # Convert sets to lists for JSON serialization
                results['changes'] = {
                    k: list(v) for k, v in changes.items()
                }
            # Get LLM analysis if available and needed
            if self.llm:
                try:
                    report = self._capture_circuit_report(circuit)
                    circuit_json = circuit.export_circuit()
                    llm_results = self.llm.analyze_circuit(report, circuit_json)
                    results['llm_analysis'] = llm_results
                    logger.info("LLM analysis completed successfully")
                except Exception as e:
                    error_msg = f"LLM analysis failed: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    results['errors'].append(error_msg)

            # Cache analysis results if enabled
            if self.config.use_cache:
                self.change_detector.cache_analysis(circuit, results)

            # Save analysis results to files
            self.save_analysis(results)
            
            return results

        except Exception as e:
            error_msg = f"Circuit analysis failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'errors': [error_msg],
                'basic_analysis': None,
                'validation_results': None,
                'llm_analysis': None
            }

    def _perform_basic_analysis(self, circuit: 'Circuit') -> Dict:
        """Perform basic circuit validation and analysis."""
        debug_logger.info("Starting basic circuit analysis")

        results = {
            'component_count': len(circuit.components),
            'net_count': len(circuit.get_nets()),
            'warnings': [],
            'suggestions': [],
            'component_details': [],
            'net_details': []
        }

        # Track seen warnings to prevent duplicates
        seen_warnings = set()

        # Analyze components
        for component in circuit.components:
            comp_info = {
                'ref': component.ref,
                'name': component.name,
                'pin_count': len(component.pins),
                'connected_pins': sum(1 for pin in component.pins.values() if pin.net)
            }
            results['component_details'].append(comp_info)
            debug_logger.debug(f"Component {component.ref}: {comp_info['connected_pins']}/{comp_info['pin_count']} pins connected")

            # Check unconnected pins
            for pin in component.pins.values():
                if not pin.net:
                    warning = f"Unconnected pin: {component.ref}.{pin.name}"
                    if warning not in seen_warnings:
                        results['warnings'].append(warning)
                        logger.warning(warning)
                        seen_warnings.add(warning)

        # Analyze nets
        for net in circuit.get_nets():
            net_info = {
                'name': net.name,
                'connected_pins': len(net.pins),
                'components': list(set(pin.parent.ref for pin in net.pins))
            }
            results['net_details'].append(net_info)
            debug_logger.debug(f"Net {net.name}: connects {len(net_info['components'])} components with {net_info['connected_pins']} pins")

        return results

    def _capture_circuit_report(self, circuit: 'Circuit') -> str:
        """Capture circuit report and BOM."""
        debug_logger.info("Capturing circuit report")
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            circuit.generate_circuit_report()
            circuit.generate_bom()

        report = buffer.getvalue()
        debug_logger.debug(f"Captured report of {len(report)} characters")
        return report

    def save_analysis(self, analysis_results: Dict) -> None:
        """Save analysis results to output directory."""
        logger.info(f"Saving analysis results to {self.output_dir}")

        try:
            # Save basic analysis
            basic_analysis_path = os.path.join(self.output_dir, 'basic_analysis.json')
            with open(basic_analysis_path, 'w') as f:
                json.dump(analysis_results['basic_analysis'], f, indent=2)
            debug_logger.debug(f"Saved basic analysis to {basic_analysis_path}")

            # Save validation results if present
            if analysis_results.get('validation_results'):
                validation_path = os.path.join(self.output_dir, 'validation_results.json')
                with open(validation_path, 'w') as f:
                    json.dump(
                        [vars(result) for result in analysis_results['validation_results']], 
                        f, 
                        indent=2
                    )

            # Save LLM analysis if available
            if analysis_results.get('llm_analysis'):
                llm_analysis_path = os.path.join(self.output_dir, 'llm_analysis.txt')
                llm_query_path = os.path.join(self.output_dir, 'llm_query.txt')

                with open(llm_analysis_path, 'w') as f:
                    f.write(analysis_results['llm_analysis']['response'])
                debug_logger.debug(f"Saved LLM analysis to {llm_analysis_path}")

                with open(llm_query_path, 'w') as f:
                    f.write(analysis_results['llm_analysis']['query'])
                debug_logger.debug(f"Saved LLM query to {llm_query_path}")

        except Exception as e:
            logger.error(f"Error saving analysis results: {str(e)}", exc_info=True)

    def get_supported_validation_rules(self) -> List[str]:
        """Get list of available validation rules."""
        return list(self.validator.rules.keys())

    def update_validation_config(self, 
                               severity: Optional[ValidationSeverity] = None,
                               categories: Optional[List[str]] = None,
                               rules: Optional[Dict[str, bool]] = None) -> None:
        """Update validation configuration."""
        if severity:
            self.config.validation_severity = severity
        if categories:
            self.config.validation_categories = categories
        if rules:
            for rule_name, enabled in rules.items():
                if enabled:
                    self.validator.enable_rule(rule_name)
                else:
                    self.validator.disable_rule(rule_name)