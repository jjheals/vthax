from openai import OpenAI


def format_prompt(inputs: dict) -> str:
    """Takes in a dict of inputs and creates a prompt based on the given inputs. 
    The inputs should match the form data and all must be included."""

    prompt_template = """
        Create a detailed operations plan for a military operation within the following parameters:
        I have the following available vehicles: {}. If a vehicle is not listed, assume I do not 
        have it. My starting location is at lat: {}, long: {}, in {}. My target is at lat: {}, 
        long: {}, which is about {} km from my starting location. I expect the following terrains: {}. 
        Use common sense when advising about vehicles and terrains. I have {} total personnel. Based 
        on previously acquired intelligence, my target time on objective is no more than {} hours, and 
        I expect {} resistance once on target. I want to conduct a {} mission, specifically {}. My 
        primary objective is to {}. {}
        Give me your plan in a pretty HTML format that I can display on a webpage. Put headers 
        in <h1> tags, and any body content in <p> tags. Just give me the content of your 
        recommendation, no disclaimers or anything extra. I do not need you to re-summarize the 
        parameters I just told you and want you to focus on detailing the specifics of successful execution.
    """.strip()

    additional_context:str = inputs.get('additional-context', '')

    return prompt_template.format(
        ', '.join(inputs.get('vehicles', [])),        # Available vehicles
        inputs['start-location'][0],               # Starting lat
        inputs['start-location'][1],               # Starting lon
        inputs.get('start-country', ''),           # Starting country
        inputs['target-location'][0],                 # Target lat
        inputs['target-location'][1],                 # Target lon
        round(inputs.get('straight-distance', -1)),   # Straight line distance from start -> target
        ', '.join(inputs.get('terrains', [])),        # Terrains along path
        inputs.get('total-personnel', 'unknown'),     # Total personnel
        inputs.get('target-time-on-obj', 'unknown'),  # Time on OBJ
        inputs.get('expected-resistance', 'unknown'), # Expected resistance
        inputs.get('strategy', 'unknown'),            # Strategy
        inputs.get('strategy-description', ''),       # Strategy description (e.g., "get on target without being seen", etc.)
        inputs.get('primary-objective', 'unknown'),   # Primary objective
        f'Here is some additional context about the mission that may be helpful in your analysis: {additional_context}' if additional_context else ''
    )


def get_chatgpt_response(prompt:str, api_key:str, model:str):
    client = OpenAI(
        api_key=api_key
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=700,
    )

    return response.choices[0].message.content