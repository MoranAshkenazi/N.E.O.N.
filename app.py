import streamlit as st
from agent import execute_single_tool, run_agent_task
from skills.voiceskill import generate_audio_b64
from styles.neon_header import load_css, render_hud, render_neon_header

st.set_page_config(
    page_title="N.E.O.N Research Protocol",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# טעינת סגנונות ועיצוב
load_css()
render_neon_header()
render_hud()


@st.cache_data(show_spinner=False)
def get_cached_audio(text: str) -> str:
  return generate_audio_b64(text)


def auto_play_audio(text: str):
  b64_audio = get_cached_audio(text)
  if b64_audio:
    st.html(f"""
            <audio autoplay style="display:none;">
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            </audio>
            """)


INTRO_MESSAGE = "N.E.O.N. core online. Tactical research systems initialized and awaiting directive."

if "messages" not in st.session_state:
  st.session_state.messages = [{"role": "assistant", "content": INTRO_MESSAGE}]
  st.session_state.spoken_intro = False
  st.session_state.pending_action = None
  st.session_state.action_counter = 0

if not st.session_state.spoken_intro:
  auto_play_audio(INTRO_MESSAGE)
  st.session_state.spoken_intro = True

for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])

# אישור אבטחה (HITL)
if st.session_state.pending_action:
  action = st.session_state.pending_action
  c = st.session_state.action_counter

  st.markdown(
      f"""
        <div class="permission-box">
            ⚠️ <strong>SECURITY AUTHORIZATION REQUIRED</strong><br>
            Action: <code>{action['tool_name']}</code><br>
            Parameters: <code>{action['tool_args']}</code>
        </div>
        """,
      unsafe_allow_html=True,
  )
  col1, col2 = st.columns([1, 1])
  with col1:
    if st.button(
        "✅ Authorize Action",
        key=f"auth_btn_{c}_{action['tool_name']}",
        use_container_width=True,
    ):
      result = execute_single_tool(action["tool_name"], action["tool_args"])
      st.session_state.messages.append({
          "role": "assistant",
          "content": (
              f"I have executed `{action['tool_name']}`. Result: {result}"
          ),
      })
      st.session_state.pending_action = None
      st.session_state.action_counter += 1
      st.rerun()
  with col2:
    if st.button(
        "❌ Deny Action",
        key=f"deny_btn_{c}_{action['tool_name']}",
        use_container_width=True,
    ):
      st.session_state.messages.append({
          "role": "assistant",
          "content": f"Action `{action['tool_name']}` was cancelled by user.",
      })
      st.session_state.pending_action = None
      st.session_state.action_counter += 1
      st.rerun()

# קלט מהמשתמש
if user_query := st.chat_input("Input command or research directive..."):
  if user_query.strip():
    st.session_state.pending_action = None
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
      st.markdown(user_query)

    with st.chat_message("assistant"):
      with st.spinner("N.E.O.N. is processing task..."):
        response = run_agent_task(
            user_prompt=user_query,
            chat_history=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ],
        )

        if response.get("status") == "requires_permission":
          st.session_state.pending_action = response
          st.rerun()
        else:
          answer = response.get("text", "")
          st.markdown(answer)
          st.session_state.messages.append(
              {"role": "assistant", "content": answer}
          )
          auto_play_audio(answer)