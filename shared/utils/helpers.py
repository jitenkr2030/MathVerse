"""
Helper Utilities Module

This module provides general-purpose helper functions for the MathVerse
platform, including ID generation, retry logic, and data manipulation.
"""

import secrets
import hashlib
import time
import random
import string
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Iterator, List, Optional, TypeVar, Union
import json
import logging


logger = logging.getLogger(__name__)


T = TypeVar("T")


def generate_unique_id(
    prefix: str = "",
    length: int = 16,
    use_hex: bool = False
) -> str:
    """
    Generate a unique identifier.
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of the random portion
        use_hex: Use hexadecimal characters
        
    Returns:
        Unique identifier string
    """
    if use_hex:
        random_part = secrets.token_hex(length // 2)
    else:
        chars = string.ascii_letters + string.digits
        random_part = "".join(secrets.choice(chars) for _ in range(length))
    
    if prefix:
        return f"{prefix}_{random_part}"
    return random_part


def generate_short_code(length: int = 8) -> str:
    """
    Generate a short alphanumeric code.
    
    Args:
        length: Code length
        
    Returns:
        Short code string
    """
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def retry_operation(
    func: Callable,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retrying a function on failure.
    
    Args:
        func: Function to wrap
        max_retries: Maximum retry attempts
        delay: Initial delay between retries
        backoff: Delay multiplier
        exceptions: Exceptions to catch
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_delay = delay
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                
                if attempt == max_retries:
                    logger.error(
                        f"Operation failed after {max_retries} retries",
                        function=func.__name__,
                        error=str(e)
                    )
                    raise
                
                logger.warning(
                    f"Operation failed, retrying in {current_delay:.2f}s",
                    function=func.__name__,
                    attempt=attempt + 1,
                    error=str(e)
                )
                
                time.sleep(current_delay)
                current_delay *= backoff
        
        raise last_exception
    
    return wrapper


def chunk_list(lst: List[T], chunk_size: int) -> Iterator[List[T]]:
    """
    Split a list into chunks.
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Yields:
        List chunks
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def flatten_dict(
    d: Dict[str, Any],
    parent_key: str = "",
    sep: str = "."
) -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for keys
        
    Returns:
        Flattened dictionary
    """
    items = {}
    
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.update(flatten_dict(value, new_key, sep))
        elif isinstance(value, list):
            for i, v in enumerate(value):
                if isinstance(v, dict):
                    items.update(flatten_dict(v, f"{new_key}[{i}]", sep))
                else:
                    items[f"{new_key}[{i}]"] = v
        else:
            items[new_key] = value
    
    return items


def deep_merge(
    base: Dict[str, Any],
    override: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        override: Dictionary to merge in
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def remove_none_values(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove None values from a dictionary.
    
    Args:
        d: Dictionary to process
        
    Returns:
        Dictionary without None values
    """
    return {k: v for k, v in d.items() if v is not None}


def group_by(
    lst: List[T],
    key_func: Callable[[T], Any]
) -> Dict[Any, List[T]]:
    """
    Group a list by a key function.
    
    Args:
        lst: List to group
        key_func: Function to extract grouping key
        
    Returns:
        Dictionary of groups
    """
    groups = {}
    
    for item in lst:
        key = key_func(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    
    return groups


def sort_dict_by_keys(
    d: Dict[str, Any],
    ascending: bool = True
) -> Dict[str, Any]:
    """
    Sort a dictionary by its keys.
    
    Args:
        d: Dictionary to sort
        ascending: Sort order
        
    Returns:
        Sorted dictionary
    }
    return dict(sorted(d.items(), key=lambda x: x[0], reverse=not ascending))


def safe_get(
    d: Dict[str, Any],
    *keys: str,
    default: Any = None
) -> Any:
    """
    Safely get a nested value from a dictionary.
    
    Args:
        d: Dictionary to search
        *keys: Keys to traverse
        default: Default value if not found
        
    Returns:
        Found value or default
    """
    current = d
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def classproperty(func: Callable) -> property:
    """
    Decorator for class properties.
    
    Args:
        func: Function to wrap
        
    Returns:
        Property descriptor
    """
    return property(classmethod(func))


def singleton(cls: type) -> type:
    """
    Decorator to make a class a singleton.
    
    Args:
        cls: Class to decorate
        
    Returns:
        Singleton class
    """
    instances = {}
    
    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return wrapper


def memoize(func: Callable) -> Callable:
    """
    Simple memoization decorator.
    
    Args:
        func: Function to memoize
        
    Returns:
        Memoized function
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    return wrapper


def rate_limiter(
    max_calls: int,
    time_window: int = 60
) -> Callable:
    """
    Decorator for rate limiting function calls.
    
    Args:
        max_calls: Maximum calls in time window
        time_window: Time window in seconds
        
    Returns:
        Rate limiting decorator
    """
    calls = []
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old calls outside time window
            calls[:] = [t for t in calls if now - t < time_window]
            
            if len(calls) >= max_calls:
                oldest = calls[0]
                wait_time = time_window - (now - oldest)
                
                if wait_time > 0:
                    time.sleep(wait_time)
            
            calls.append(time.time())
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def timer(func: Callable) -> Callable:
    """
    Decorator to time function execution.
    
    Args:
        func: Function to time
        
    Returns:
        Timed function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        
        logger.info(
            f"Function {func.__name__} took {(end - start) * 1000:.2f}ms"
        )
        
        return result
    
    return wrapper


def validate_types(**type_hints):
    """
    Decorator for runtime type validation.
    
    Args:
        **type_hints: Type hints for validation
        
    Returns:
        Validation decorator
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Validate types
            for name, expected_type in type_hints.items():
                value = bound.arguments.get(name)
                
                if value is not None and not isinstance(value, expected_type):
                    raise TypeError(
                        f"Argument '{name}' must be {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class LazyLoader:
    """
    Lazy loader for expensive imports.
    """
    
    def __init__(self, import_path: str):
        """
        Initialize lazy loader.
        
        Args:
            import_path: Module path to import
        """
        self.import_path = import_path
        self._module = None
    
    def __getattr__(self, name: str) -> Any:
        """Lazy import and return attribute."""
        if self._module is None:
            import importlib
            self._module = importlib.import_module(self.import_path)
        
        return getattr(self._module, name)


def to_camel_case(snake_str: str) -> str:
    """
    Convert snake_case to camelCase.
    
    Args:
        snake_str: Snake case string
        
    Returns:
        Camel case string
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_snake_case(camel_str: str) -> str:
    """
    Convert camelCase to snake_case.
    
    Args:
        camel_str: Camel case string
        
    Returns:
        Snake case string
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def json_dumps(obj: Any, **kwargs) -> str:
    """
    Custom JSON serialization with datetime support.
    
    Args:
        obj: Object to serialize
        **kwargs: Additional JSON arguments
        
    Returns:
        JSON string
    """
    def default_serializer(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f"Object of type {type(o)} is not JSON serializable")
    
    return json.dumps(obj, default=default_serializer, **kwargs)
