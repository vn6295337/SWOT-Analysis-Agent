from langchain_groq import ChatGroq
from langsmith import traceable

@traceable(name="Editor")
def editor_node(state, workflow_id=None, progress_store=None):
    """
    Editor node that revises the SWOT draft based on critique feedback.
    Increments the revision count and returns the improved draft.
    """
    # Update progress if tracking is enabled
    if workflow_id and progress_store:
        progress_store[workflow_id].update({
            "current_step": "Editor",
            "revision_count": state.get("revision_count", 0),
            "score": state.get("score", 0)
        })
    
    llm = ChatGroq(temperature=0, model="llama-3.1-8b-instant")
    
    # Prepare the revision prompt
    prompt = f"""
Revise this SWOT draft based on the following critique:

Draft:
{state['draft_report']}

Critique:
{state['critique']}

Strategic Focus: Cost Leadership

Please improve the draft by:
1. Adding specific facts and numbers if missing
2. Ensuring all 4 SWOT sections are present and complete
3. Making sure strengths/opportunities are distinct from weaknesses/threats
4. Aligning with the Cost Leadership strategic focus

Return only the improved SWOT analysis in the same format.
"""
    
    # Get the revised draft from LLM
    response = llm.invoke(prompt)
    
    # Update the state with revised draft and increment revision count
    state["draft_report"] = response.content
    state["revision_count"] = state.get("revision_count", 0) + 1
    
    # Update progress with new revision count
    if workflow_id and progress_store:
        progress_store[workflow_id].update({
            "current_step": "Editor",
            "revision_count": state["revision_count"],
            "score": state.get("score", 0)
        })
    
    return state