// college_predictor_api.js
const express = require('express');
const XLSX = require('xlsx');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

const PORT = 3000;

// Load Excel data (skip first row)
const workbook = XLSX.readFile('./ts.xlsx');
const sheet = workbook.Sheets[workbook.SheetNames[0]];
const rawData = XLSX.utils.sheet_to_json(sheet, { defval: '', range: 1 }); // Skip title row

// Clean column names and map to unified keys
const data = rawData.map(row => ({
  INSTCODE: row['Inst\n Code'],
  COLLEGE_NAME: row['Institute Name'],
  PLACE: row['Place'],
  DIST: row['Dist \nCode'],
  COED: row['Co Education'],
  TYPE: row['College Type'],
  INST_REG: row['Year of Estab'],
  BRANCH: row['Branch Code'],
  BRANCH_NAME: row['Branch Name'],

  OC_BOYS: parseInt(row['OC \nBOYS']) || null,
  OC_GIRLS: parseInt(row['OC \nGIRLS']) || null,
  BCA_BOYS: parseInt(row['BC_A \nBOYS']) || null,
  BCA_GIRLS: parseInt(row['BC_A \nGIRLS']) || null,
  BCB_BOYS: parseInt(row['BC_B \nBOYS']) || null,
  BCB_GIRLS: parseInt(row['BC_B \nGIRLS']) || null,
  BCC_BOYS: parseInt(row['BC_C \nBOYS']) || null,
  BCC_GIRLS: parseInt(row['BC_C \nGIRLS']) || null,
  BCD_BOYS: parseInt(row['BC_D \nBOYS']) || null,
  BCD_GIRLS: parseInt(row['BC_D \nGIRLS']) || null,
  BCE_BOYS: parseInt(row['BC_E \nBOYS']) || null,
  BCE_GIRLS: parseInt(row['BC_E \nGIRLS']) || null,
  SC_BOYS: parseInt(row['SC \nBOYS']) || null,
  SC_GIRLS: parseInt(row['SC \nGIRLS']) || null,
  ST_BOYS: parseInt(row['ST \nBOYS']) || null,
  ST_GIRLS: parseInt(row['ST \nGIRLS']) || null,
  OC_EWS_BOYS: parseInt(row['EWS \nGEN OU']) || null,
  OC_EWS_GIRLS: parseInt(row['EWS \nGIRLS OU']) || null,
  COLLFEE: parseInt(row['Tuition Fee']) || null,
  AFFL: row['Affiliated To']
}));

console.log("✅ Excel rows loaded:", data.length);

// API route
app.post('/predict', (req, res) => {
  const { rank, category, gender, district, branch, inst_reg } = req.body;
  if (!rank || !category || !gender) {
    return res.status(400).json({ error: 'Missing input' });
  }

  const key = `${category.toUpperCase()}_${gender.toUpperCase()}`;
  console.log("\n📥 Received request with:", req.body);
  console.log("🔑 Using cutoff key:", key);

  let result = data.filter(row => {
    const closingRank = row[key];
    return typeof closingRank === 'number' &&
           closingRank >= rank - 10000 &&
           closingRank <= rank + 20000;
  });
  console.log("🔍 After rank filter:", result.length);

  if (branch) {
    result = result.filter(row => row.BRANCH && row.BRANCH.toUpperCase() === branch.toUpperCase());
    console.log("🔎 After branch filter:", result.length);
  }
  if (district) {
    result = result.filter(row => row.DIST && row.DIST.toUpperCase() === district.toUpperCase());
    console.log("🏙️ After district filter:", result.length);
  }
  if (inst_reg) {
    result = result.filter(row => row.INST_REG && row.INST_REG.toString() === inst_reg.toString());
    console.log("🏛️ After year filter:", result.length);
  }

  result.sort((a, b) => (a[key] || Infinity) - (b[key] || Infinity));

  console.log("📦 Final result count:", result.length);
  res.json({ result, key });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});
