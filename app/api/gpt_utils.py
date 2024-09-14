from openai import OpenAI


def format_prompt(inputs: dict) -> str:
    """Takes in a dict of inputs and creates a prompt based on the given inputs. 
    The inputs should match the form data and all must be included."""

    prompt_template = """
        I am conducting a military operation. I have the following available vehicles: {}.
        My starting location is at lat: {}, long: {}, in {}. My target is at lat: {}, long: {}, 
        which is about {} km from my starting location. I expect the following terrains: {}.
        I have {} total personnel. Based on previously acquired intelligence, my target time 
        on objective is {} hours, and I expect {} resistance once on target. I want to conduct 
        a {} mission, specifically {}. My primary objective is to {}.
        Create a detailed plan for me to conduct an operation under these circumstances. Give 
        me the response in a pretty HTML format that I can display on a webpage, with bolded 
        headers etc. Put headers in <h1> tags, and any body content in <p> tags. Just give me
        the content of your recommendation, no disclaimers or anything extra. I want as much
        detail as possible, especailly around the execution of the operation.
    """.strip()

    return prompt_template.format(
        ', '.join(inputs.get('vehicles', [])),        # Available vehicles
        inputs['start-location'][0],               # Starting lat
        inputs['start-location'][1],               # Starting lon
        inputs.get('start-country', ''),           # Starting country
        inputs['target-location'][0],                 # Target lat
        inputs['target-location'][1],                 # Target lon
        inputs.get('straight-distance', 'unknown'),   # Straight line distance from start -> target
        ', '.join(inputs.get('terrains', [])),        # Terrains along path
        inputs.get('total-personnel', 'unknown'),     # Total personnel
        inputs.get('target-time-on-obj', 'unknown'),  # Time on OBJ
        inputs.get('expected-resistance', 'unknown'), # Expected resistance
        inputs.get('strategy', 'unknown'),            # Strategy
        inputs.get('strategy-description', ''),       # Strategy description (e.g., "get on target without being seen", etc.)
        inputs.get('primary-objective', 'unknown')    # Primary objective
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
        max_tokens=500,
    )

    return response.choices[0].message.content