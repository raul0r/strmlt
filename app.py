import streamlit as st
import ollama
import json
import time
from datetime import datetime

def classify_and_summarize_ollama(ticket_text, model='llama3'):
    """
    Summarizes and classifies a support ticket using a local Ollama model.

    Args:
        ticket_text: The text of the support ticket.
        model: The name of the Ollama model to use.

    Returns:
        A dictionary containing the summary and type of the ticket.
    """
    prompt = f"""
    Summarize the following support ticket and classify it.
    Respond in JSON with two keys: "summary" and "type".
    The "type" should be one of the following: "bug", "feature", or "billing".

    Ticket: {ticket_text}
    """

    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            format='json'  # This ensures the output is a JSON string
        )

        # The response content is a JSON string, so we need to parse it
        result = json.loads(response['message']['content'])
        return result

    except Exception as e:
        return {"error": str(e)}

def get_available_models():
    """Get list of available Ollama models"""
    try:
        models = ollama.list()
        return [model['name'] for model in models['models']]
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return ['llama3']  # Default fallback

def main():
    st.set_page_config(
        page_title="Support Ticket Assistant",
        page_icon="🎫",
        layout="wide"
    )

    st.title("🎫 Support Ticket Assistant")
    st.markdown("**Classify and summarize support tickets using local Ollama models**")

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        available_models = get_available_models()
        selected_model = st.selectbox(
            "Select Model:",
            available_models,
            index=0 if available_models else 0
        )
        
        st.markdown("---")
        
        # Statistics
        st.header("📊 Statistics")
        if 'processed_tickets' not in st.session_state:
            st.session_state.processed_tickets = 0
        
        st.metric("Processed Tickets", st.session_state.processed_tickets)
        
        # Clear history button
        if st.button("Clear History"):
            if 'ticket_history' in st.session_state:
                st.session_state.ticket_history = []
            st.session_state.processed_tickets = 0
            st.success("History cleared!")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📝 Ticket Input")
        
        # Ticket input methods
        input_method = st.radio(
            "Choose input method:",
            ["Type/Paste", "Example Tickets"]
        )
        
        if input_method == "Type/Paste":
            ticket_text = st.text_area(
                "Enter support ticket text:",
                height=150,
                placeholder="Paste your support ticket here..."
            )
        else:
            # Example tickets
            examples = {
                "Billing Issue": "My invoice says I owe $500, but I already paid last week. Can you please check my payment status?",
                "Bug Report": "The login button doesn't work on mobile devices. When I tap it, nothing happens and I can't access my account.",
                "Feature Request": "It would be great if you could add a dark mode option to the dashboard. Many users have been requesting this feature."
            }
            
            selected_example = st.selectbox("Select an example:", list(examples.keys()))
            ticket_text = st.text_area(
                "Example ticket text:",
                value=examples[selected_example],
                height=150
            )

        # Process button
        if st.button("🔍 Analyze Ticket", type="primary"):
            if ticket_text.strip():
                with st.spinner("Analyzing ticket..."):
                    result = classify_and_summarize_ollama(ticket_text, selected_model)
                    
                    if result and "error" not in result:
                        st.session_state.processed_tickets += 1
                        
                        # Store in history
                        if 'ticket_history' not in st.session_state:
                            st.session_state.ticket_history = []
                        
                        st.session_state.ticket_history.append({
                            'timestamp': datetime.now(),
                            'ticket': ticket_text,
                            'result': result,
                            'model': selected_model
                        })
                        
                        # Display results
                        st.success("Analysis complete!")
                        
                        # Results in columns
                        res_col1, res_col2 = st.columns(2)
                        
                        with res_col1:
                            st.subheader("📋 Summary")
                            st.write(result.get('summary', 'No summary available'))
                        
                        with res_col2:
                            st.subheader("🏷️ Classification")
                            ticket_type = result.get('type', 'unknown')
                            
                            # Color coding for different types
                            if ticket_type == 'bug':
                                st.error(f"**{ticket_type.upper()}**")
                            elif ticket_type == 'feature':
                                st.info(f"**{ticket_type.upper()}**")
                            elif ticket_type == 'billing':
                                st.warning(f"**{ticket_type.upper()}**")
                            else:
                                st.write(f"**{ticket_type.upper()}**")
                    
                    else:
                        st.error(f"Error processing ticket: {result.get('error', 'Unknown error')}")
            else:
                st.warning("Please enter a ticket text to analyze.")

    with col2:
        st.header("📈 Results Overview")
        
        # Display type distribution if we have history
        if 'ticket_history' in st.session_state and st.session_state.ticket_history:
            types = [item['result'].get('type', 'unknown') for item in st.session_state.ticket_history]
            type_counts = {t: types.count(t) for t in set(types)}
            
            st.subheader("Type Distribution")
            for ticket_type, count in type_counts.items():
                st.write(f"**{ticket_type.capitalize()}**: {count}")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        if st.button("📋 View History"):
            st.session_state.show_history = True
        
        if st.button("💾 Export Results"):
            if 'ticket_history' in st.session_state and st.session_state.ticket_history:
                # Create export data
                export_data = []
                for item in st.session_state.ticket_history:
                    export_data.append({
                        'timestamp': item['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        'type': item['result'].get('type', 'unknown'),
                        'summary': item['result'].get('summary', ''),
                        'original_ticket': item['ticket'][:100] + '...' if len(item['ticket']) > 100 else item['ticket']
                    })
                
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"ticket_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No data to export")

    # History section
    if st.session_state.get('show_history', False):
        st.header("📚 Ticket History")
        
        if 'ticket_history' in st.session_state and st.session_state.ticket_history:
            for i, item in enumerate(reversed(st.session_state.ticket_history)):
                with st.expander(f"Ticket {len(st.session_state.ticket_history) - i} - {item['result'].get('type', 'unknown').upper()} - {item['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    st.write("**Original Ticket:**")
                    st.write(item['ticket'])
                    st.write("**Summary:**")
                    st.write(item['result'].get('summary', 'No summary'))
                    st.write(f"**Model Used:** {item['model']}")
        else:
            st.info("No tickets processed yet.")
        
        if st.button("Hide History"):
            st.session_state.show_history = False

    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and Ollama")

if __name__ == "__main__":
    main()
