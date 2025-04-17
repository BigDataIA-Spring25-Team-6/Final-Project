import streamlit as st
import requests

st.set_page_config(page_title="FAQ Assistant", layout="centered")

st.title("🔍 FAQ Agent - Interview Help")

# Predefined options for selectboxes
roles = [
    "Software Engineer", "Data Scientist", "Product Manager",
    "DevOps Engineer", "Backend Developer", "Frontend Engineer"
]

companies = [
    "Google", "Amazon", "Meta", "Microsoft", "Netflix", "OpenAI"
]

# Dropdowns for role and company
role = st.selectbox("Select Role", roles)
company = st.selectbox("Select Company", companies)

# Textbox for user query
query = st.text_area("Type your interview-related question", "What are some interview questions?")

# Button and backend call
if st.button("Ask"):
    with st.spinner("Fetching answer..."):
        try:
            res = requests.post(
                "http://localhost:8000/faq",
                json={"query": query, "role": role, "company": company}
            )
            if res.status_code == 200:
                result = res.json()["data"]
                st.success("✅ Answer fetched!")
                st.markdown(f"### 📌 Query\n{result['faq_query']}")
                st.markdown(f"### 🔍 Role\n{result['job_role']}")
                st.markdown(f"### 🏢 Company\n{result['company']}")
                st.markdown("### 🧠 FAQ Answer")
                st.markdown(result["faq_response"]["tasks_output"][0]["raw"])

                if "summary" in result:
                    st.markdown("### 📋 Summary")
                    st.markdown(result["summary"])

            elif res.status_code == 400:
                # 🟡 Handle irrelevant/low-score queries
                error_message = res.json().get("detail", "❌ Your question was not relevant.")
                st.warning(f"⚠️ {error_message}")

            else:
                # 🔴 Unexpected errors (e.g., 500)
                st.error(f"❌ Server Error: {res.json().get('detail', 'Unknown error')}")

        except Exception as e:
            st.error(f"🚨 Request failed: {str(e)}")

        #     else:
        #         st.error(f"❌ Error: {res.json()['detail']}")
        # except Exception as e:
        #     st.error(f"🚨 Request failed: {str(e)}")
