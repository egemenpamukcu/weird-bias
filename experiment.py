"""
Core experiment functions for measuring WEIRD bias drift in LLMs.

All functions are designed to be called from a notebook.
"""

from openai import OpenAI

from prompts import (
    WVS_QUESTIONS,
    BOT_SYSTEM_PROMPT,
    BOT_SURVEY_PROMPT,
    USER_SYSTEM_PROMPT,
    CONVERSATION_TOPIC,
    SurveyResponse,
)


def measure_wvs(
    client: OpenAI,
    model: str,
    conversation_history: list[dict],
) -> dict[str, float]:
    """
    Administer WVS questions to the LLM and extract numeric responses.
    
    Args:
        client: OpenAI client instance
        model: Model name (e.g., "gpt-4o")
        conversation_history: Prior conversation context (empty list for baseline)
    
    Returns:
        Dict mapping question_id to numeric score
    """
    scores = {}
    
    for question in WVS_QUESTIONS:
        # Build messages: system prompt + conversation history + WVS question
        messages = [{"role": "system", "content": BOT_SURVEY_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": question["text"]})
        
        response = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=SurveyResponse,
        )
        survey_response: SurveyResponse = response.choices[0].message.parsed
        print(f"{question['id']}: {survey_response.response} (caveat: {survey_response.caveat})")
        
        scores[question["id"]] = float(survey_response.response)
    
    return scores


def run_conversation(
    client: OpenAI,
    bot_model: str,
    user_model: str,
    n_turns: int,
) -> list[dict]:
    """
    Run N back-and-forth exchanges between bot and user LLMs.
    
    The user LLM initiates with the conversation topic.
    
    Args:
        client: OpenAI client instance
        bot_model: Model for the bot LLM (the one we measure)
        user_model: Model for the user LLM (non-WEIRD prompted)
        n_turns: Number of back-and-forth exchanges
    
    Returns:
        Conversation history as list of {"role": ..., "content": ...} dicts
        (from the bot's perspective: user messages are "user", bot messages are "assistant")
    """
    # Conversation history from bot's perspective
    bot_history = []
    # Conversation history from user's perspective (roles are flipped)
    user_history = []
    
    # User LLM initiates with the topic
    user_messages = [
        {"role": "system", "content": USER_SYSTEM_PROMPT},
        {"role": "user", "content": f"Start a conversation about: {CONVERSATION_TOPIC}"},
    ]
    response = client.chat.completions.create(model=user_model, messages=user_messages)
    user_message = response.choices[0].message.content
    
    # Add to histories
    bot_history.append({"role": "user", "content": user_message})
    user_history.append({"role": "assistant", "content": user_message})
    
    # Alternate turns
    for _ in range(n_turns):
        # Bot responds
        bot_messages = [{"role": "system", "content": BOT_SYSTEM_PROMPT}] + bot_history
        response = client.chat.completions.create(model=bot_model, messages=bot_messages)
        bot_message = response.choices[0].message.content
        
        bot_history.append({"role": "assistant", "content": bot_message})
        user_history.append({"role": "user", "content": bot_message})
        
        # User responds
        user_messages = [{"role": "system", "content": USER_SYSTEM_PROMPT}] + user_history
        response = client.chat.completions.create(model=user_model, messages=user_messages)
        user_message = response.choices[0].message.content
        
        bot_history.append({"role": "user", "content": user_message})
        user_history.append({"role": "assistant", "content": user_message})
    
    return bot_history


def run_experiment(
    api_key: str,
    bot_model: str = "gpt-4o",
    user_model: str = "gpt-4o",
    n_turns: int = 5,
) -> dict:
    """
    Run the full experiment pipeline.
    
    Args:
        api_key: OpenAI API key
        bot_model: Model for the bot LLM (the one we measure for drift)
        user_model: Model for the user LLM (prompted with non-WEIRD values)
        n_turns: Number of conversation turns
    
    Returns:
        Dict with baseline scores, post scores, and conversation
    """
    client = OpenAI(api_key=api_key)
    
    # 1. Baseline measurement (empty conversation history)
    baseline = measure_wvs(client, bot_model, conversation_history=[])
    
    # 2. Run conversation
    conversation = run_conversation(client, bot_model, user_model, n_turns)
    
    # 3. Post-interaction measurement (with conversation history)
    post = measure_wvs(client, bot_model, conversation_history=conversation)
    
    return {
        "baseline": baseline,
        "post": post,
        "conversation": conversation,
        "config": {
            "bot_model": bot_model,
            "user_model": user_model,
            "n_turns": n_turns,
        },
    }

