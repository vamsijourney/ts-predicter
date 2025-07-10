import streamlit as st
import pandas as pd
import numpy as np
import io
from fpdf import FPDF

EXCEL_FILE = '03_TGEAPCET_2024_FinalPhase_LastRanks (2).xlsx'

def load_data():
    df = pd.read_excel(EXCEL_FILE)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    df.columns = df.columns.str.strip()
    if 'Branch Code' in df.columns:
        df['Branch Code'] = df['Branch Code'].astype(str).str.strip()
    return df

def get_rank_columns(df):
    return [col for col in df.columns if '_BOYS' in col or '_GIRLS' in col]

def generate_pdf(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'TG EAPCET 2024 – College Prediction by Vamsi Journey', ln=True, align='C')
    pdf.ln(3)

    pdf.set_font('Arial', '', 8)
    pdf.multi_cell(0, 5, "Note: These predictions are based on past closing ranks. Always verify with official counselling data.")
    pdf.ln(4)

    column_widths = {
        'Inst Code': 20,
        'Institute Name': 60,
        'Branch Code': 20,
        'Branch Name': 40,
        'Dist Code': 25,
        'Place': 25,
        'College Type': 25,
        'Co Education': 20,
        'Year of Estab': 20,
        'Affiliated To': 25,
        'Tution Fee': 20,
    }

    # Add cutoff column (e.g., OC_BOYS)
    rank_col = [col for col in df.columns if '_BOYS' in col or '_GIRLS' in col]
    if rank_col:
        column_widths[rank_col[0]] = 25

    all_columns = df.columns.tolist()
    for col in all_columns:
        if col not in column_widths:
            column_widths[col] = 25

    pdf.set_font('Arial', 'B', 8)
    for col in df.columns:
        pdf.cell(column_widths[col], 6, str(col)[:30], border=1, align='C')
    pdf.ln()

    pdf.set_font('Arial', '', 7)
    for _, row in df.iterrows():
        for col in df.columns:
            text = str(row[col]) if pd.notnull(row[col]) else ''
            if len(text) > 50:
                text = text[:47] + '...'
            pdf.cell(column_widths[col], 6, text, border=1, align='C')
        pdf.ln()

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return io.BytesIO(pdf_bytes)

def main():
    st.set_page_config(page_title="TG EAPCET Predictor", layout="wide")
    st.title("📊 TG EAPCET 2024 – College Predictor (Vamsi Journey)")

    df = load_data()
    rank_columns = get_rank_columns(df)

    with st.form("predict_form"):
        st.subheader("🔍 Enter Your Details")
        selected_key = st.selectbox("🎯 Select Category + Gender (e.g., OC_BOYS):", rank_columns)
        rank = st.text_input("🏅 Enter Your EAPCET Rank (Required):", placeholder="e.g., 32000")

        branches = sorted(df['Branch Code'].dropna().unique())
        selected_branches = st.multiselect("📚 Select Branch(es):", branches)

        districts = sorted(df['Dist Code'].dropna().unique())
        selected_dists = st.multiselect("🌍 Select District(s):", districts)

        regions = sorted(df['A_REG'].dropna().unique()) if 'A_REG' in df.columns else []
        selected_regions = st.multiselect("📍 Select Region(s):", regions)

        submit = st.form_submit_button("🚀 Predict Colleges")

    if submit:
        if not rank or not rank.isdigit():
            st.error("❌ Please enter a valid numeric rank.")
            return

        rank = int(rank)
        df[selected_key] = pd.to_numeric(df[selected_key], errors='coerce')
        filtered_df = df.dropna(subset=[selected_key])

        # Apply filters
        if selected_branches:
            filtered_df = filtered_df[filtered_df['Branch Code'].isin(selected_branches)]
        if selected_dists:
            filtered_df = filtered_df[filtered_df['Dist Code'].isin(selected_dists)]
        if selected_regions:
            filtered_df = filtered_df[filtered_df['A_REG'].isin(selected_regions)]

        lower = max(rank - 5000, 0)
        upper = rank + 20000
        result_df = filtered_df[
            (filtered_df[selected_key] >= lower) & (filtered_df[selected_key] <= upper)
        ]

        result_df = result_df[
            ['Inst Code', 'Institute Name', 'Branch Code', 'Branch Name', 'Dist Code',
             'Place', 'College Type', 'Co Education', 'Year of Estab',
             'Affiliated To', selected_key, 'Tution Fee']
        ]

        if result_df.empty:
            st.warning("⚠️ No exact matches found for your filters. Try changing filters.")
        else:
            st.success(f"✅ Found {len(result_df)} matching colleges!")
            st.dataframe(result_df, use_container_width=True)

            pdf_bytes = generate_pdf(result_df)
            st.download_button("📥 Download Results as PDF", data=pdf_bytes,
                               file_name="TG_EAPCET_Predictor_Results.pdf",
                               mime="application/pdf")

if __name__ == '__main__':
    main()
