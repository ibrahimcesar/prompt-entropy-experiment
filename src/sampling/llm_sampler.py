"""
LLM sampling utilities for GPT-4 and Claude models
"""

import os
from typing import List, Dict, Optional, Literal
from tqdm import tqdm
import time

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


ModelType = Literal[
    "gpt-4",
    "gpt-4-turbo",
    "gpt-4o",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3.5-sonnet",
    "claude-3.5-haiku",
]


def sample_responses(
    prompt: str,
    model: ModelType = "gpt-4",
    n: int = 30,
    temperature: float = 1.0,
    max_tokens: Optional[int] = None,
    api_key: Optional[str] = None,
    show_progress: bool = True,
    delay_between_requests: float = 0.1,
) -> List[str]:
    """
    Sample multiple responses from an LLM with specified parameters

    Args:
        prompt: The prompt to send to the model
        model: Model to use ('gpt-4', 'gpt-4-turbo', 'claude-3-opus', 'claude-3-sonnet')
        n: Number of samples to generate
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens in response (None for default)
        api_key: Optional API key (will use environment variable if not provided)
        show_progress: Whether to show progress bar
        delay_between_requests: Delay in seconds between API requests

    Returns:
        List of response strings

    Raises:
        ValueError: If model is not supported or API client not available
        ImportError: If required package is not installed
    """
    if model.startswith("gpt"):
        return _sample_openai(
            prompt, model, n, temperature, max_tokens, api_key,
            show_progress, delay_between_requests
        )
    elif model.startswith("claude"):
        return _sample_anthropic(
            prompt, model, n, temperature, max_tokens, api_key,
            show_progress, delay_between_requests
        )
    else:
        raise ValueError(f"Unsupported model: {model}")


def _sample_openai(
    prompt: str,
    model: str,
    n: int,
    temperature: float,
    max_tokens: Optional[int],
    api_key: Optional[str],
    show_progress: bool,
    delay: float,
) -> List[str]:
    """Sample responses from OpenAI GPT models"""
    if OpenAI is None:
        raise ImportError("openai package not installed. Run: pip install openai")

    # Initialize client
    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    responses = []
    iterator = tqdm(range(n), desc=f"Sampling {model}") if show_progress else range(n)

    for _ in iterator:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            responses.append(response.choices[0].message.content)

            # Add delay to avoid rate limits
            if delay > 0:
                time.sleep(delay)

        except Exception as e:
            if show_progress:
                tqdm.write(f"Error sampling response: {e}")
            raise

    return responses


def _sample_anthropic(
    prompt: str,
    model: str,
    n: int,
    temperature: float,
    max_tokens: Optional[int],
    api_key: Optional[str],
    show_progress: bool,
    delay: float,
) -> List[str]:
    """Sample responses from Anthropic Claude models"""
    if Anthropic is None:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    # Initialize client
    client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))

    # Map model names to API format
    model_map = {
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
        "claude-3.5-haiku": "claude-3-5-haiku-20241022",
    }
    api_model = model_map.get(model, model)

    # Default max_tokens for Claude (required parameter)
    if max_tokens is None:
        max_tokens = 4096

    responses = []
    iterator = tqdm(range(n), desc=f"Sampling {model}") if show_progress else range(n)

    for _ in iterator:
        try:
            response = client.messages.create(
                model=api_model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            responses.append(response.content[0].text)

            # Add delay to avoid rate limits
            if delay > 0:
                time.sleep(delay)

        except Exception as e:
            if show_progress:
                tqdm.write(f"Error sampling response: {e}")
            raise

    return responses


def sample_responses_batch(
    prompts: List[str],
    model: ModelType = "gpt-4",
    n_per_prompt: int = 30,
    temperature: float = 1.0,
    max_tokens: Optional[int] = None,
    api_key: Optional[str] = None,
    show_progress: bool = True,
    delay_between_requests: float = 0.1,
) -> Dict[str, List[str]]:
    """
    Sample responses for multiple prompts

    Args:
        prompts: List of prompts
        model: Model to use
        n_per_prompt: Number of samples per prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        api_key: Optional API key
        show_progress: Whether to show progress bar
        delay_between_requests: Delay between API requests

    Returns:
        Dictionary mapping prompts to lists of responses
    """
    results = {}

    prompt_iterator = (
        tqdm(prompts, desc="Processing prompts")
        if show_progress else prompts
    )

    for prompt in prompt_iterator:
        if show_progress:
            tqdm.write(f"\nSampling for prompt: {prompt[:50]}...")

        responses = sample_responses(
            prompt=prompt,
            model=model,
            n=n_per_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            show_progress=show_progress,
            delay_between_requests=delay_between_requests,
        )

        results[prompt] = responses

    return results


def get_embeddings(
    texts: List[str],
    model: str = "text-embedding-3-small",
    api_key: Optional[str] = None,
    batch_size: int = 100,
    show_progress: bool = True,
) -> List[List[float]]:
    """
    Get embeddings for a list of texts using OpenAI's embedding models

    Args:
        texts: List of texts to embed
        model: Embedding model to use
        api_key: Optional API key
        batch_size: Number of texts to embed per request
        show_progress: Whether to show progress bar

    Returns:
        List of embedding vectors
    """
    if OpenAI is None:
        raise ImportError("openai package not installed. Run: pip install openai")

    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    embeddings = []

    # Process in batches
    iterator = (
        tqdm(range(0, len(texts), batch_size), desc="Getting embeddings")
        if show_progress else range(0, len(texts), batch_size)
    )

    for i in iterator:
        batch = texts[i:i + batch_size]

        try:
            response = client.embeddings.create(
                input=batch,
                model=model,
            )

            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)

        except Exception as e:
            if show_progress:
                tqdm.write(f"Error getting embeddings: {e}")
            raise

    return embeddings
