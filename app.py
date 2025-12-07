
import streamlit as st
from bot import build_agent

st.title("🚗 BOT PELAYANAN PEMBELIAN MOBIL")

if "agent" not in st.session_state:
    st.session_state.agent = build_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

agent = st.session_state.agent

if st.button("🔄 Reset Chat"):
    st.session_state.messages = []
    st.session_state.agent = build_agent()


user_input = st.chat_input("Tanyakan tentang mobil...")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Sedang memproses..."):
        ai_output = ""

        for step in agent.stream({"input": user_input}):
            if "actions" in step:
                for action in step["actions"]:
                    tool_block = f"""
                    <div style="font-size:13px; background:#eef3ff; padding:8px; border-left:4px solid #1d4ed8; margin:4px 0;">
                        🛠 <b>{action.tool}</b>: <code>{action.tool_input}</code>
                    </div>
                    """

                    st.session_state.messages.append({"role": "assistant", "content": tool_block})
                    with st.chat_message("assistant"):
                        st.markdown(tool_block, unsafe_allow_html=True)

            if "output" in step:
                ai_output = step["output"]

    st.session_state.messages.append({"role": "assistant", "content": ai_output})
    with st.chat_message("assistant"):
        st.markdown(ai_output, unsafe_allow_html=True)
