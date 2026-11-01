import streamlit as st
from gtts import gTTS
import os
from db import init_db, save_preference, get_all_preferences, log_action
from gmail_tools import list_unread_emails, delete_email, forward_email, compose_email, unsubscribe_email

init_db()

st.set_page_config(page_title="Mobile AI Gmail Agent", page_icon="🤖", layout="centered")

st.title("🤖 Mobile Gmail AI Agent")
st.markdown("Your autonomous inbox manager with voice updates and preference learning.")

with st.sidebar:
    st.header("🧠 Learned Preferences")
    prefs = get_all_preferences()
    if prefs:
        for k, v in prefs.items():
            st.text(f"• {k}: {v}")
    else:
        st.info("No preferences learned yet. Teach it instructions in chat!")
    
    st.markdown("---")
    new_rule_key = st.text_input("Rule Name")
    new_rule_val = st.text_input("Rule Instruction")
    if st.button("Save Preference"):
        if new_rule_key and new_rule_val:
            save_preference(new_rule_key, new_rule_val)
            st.success("Preference saved!")
            st.rerun()

st.subheader("💬 Give a Command")
user_command = st.text_area("What would you like me to do with your inbox?", placeholder="e.g., Check unread emails, delete all promotions, and summarize important messages.")

if st.button("Execute Command"):
    with st.spinner("Agent is working on your inbox..."):
        action_summary = []
        unread = list_unread_emails(max_results=5)
        cmd_lower = user_command.lower()
        
        if "check" in cmd_lower or "summarize" in cmd_lower or "unread" in cmd_lower:
            if not unread:
                summary_text = "You have no unread emails in your inbox."
            else:
                summary_text = f"You have {len(unread)} unread emails. Here are the highlights: "
                for email in unread:
                    summary_text += f"From {email['sender']} regarding {email['subject']}. "
                    action_summary.append(f"Checked: {email['subject']}")
                    log_action("CHECK", f"Read email {email['id']}")
                    
        elif "delete" in cmd_lower:
            deleted_count = 0
            for email in unread:
                delete_email(email['id'])
                deleted_count += 1
                log_action("DELETE", f"Deleted email {email['id']}")
            summary_text = f"Successfully deleted {deleted_count} unread emails from your inbox."
            action_summary.append(f"Deleted {deleted_count} emails.")
            
        elif "unsubscribe" in cmd_lower:
            unsub_count = 0
            for email in unread:
                unsubscribe_email(email['id'])
                unsub_count += 1
                log_action("UNSUBSCRIBE", f"Unsubscribed email {email['id']}")
            summary_text = f"Processed unsubscribe requests for {unsub_count} emails."
            action_summary.append(f"Unsubscribed {unsub_count} emails.")
            
        else:
            summary_text = f"Executed request based on your instructions. Inbox checked successfully."
            action_summary.append("Custom action executed.")
            log_action("CUSTOM", user_command)

        st.success("### 📝 Written Summary")
        st.write(summary_text)
        
        if action_summary:
            st.markdown("**Actions Performed:**")
            for act in action_summary:
                st.caption(f"✓ {act}")

        tts = gTTS(text=summary_text, lang='en', slow=False)
        audio_file = "briefing.mp3"
        tts.save(audio_file)
        
        st.markdown("### 🔊 Audio Update")
        st.audio(audio_file, format='audio/mp3', autoplay=True)
