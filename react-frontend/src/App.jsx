import { useState } from 'react';
import './index.css';

function App() {
  const [formData, setFormData] = useState({
    customerID: 'CUST-001',
    gender: 'Male',
    SeniorCitizen: '0',
    Partner: 'Yes',
    Dependents: 'No',
    tenure: '12',
    PhoneService: 'Yes',
    MultipleLines: 'No',
    InternetService: 'Fiber optic',
    OnlineSecurity: 'No',
    OnlineBackup: 'Yes',
    DeviceProtection: 'No',
    TechSupport: 'No',
    StreamingTV: 'No',
    StreamingMovies: 'No',
    Contract: 'Month-to-month',
    PaperlessBilling: 'Yes',
    PaymentMethod: 'Electronic check',
    MonthlyCharges: '50.0',
    TotalCharges: '600.0'
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      // In production, configure proxy in vite.config.js or use full URL
      const response = await fetch('http://localhost:8000/predict_churn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          SeniorCitizen: parseInt(formData.SeniorCitizen),
          tenure: parseInt(formData.tenure),
          MonthlyCharges: parseFloat(formData.MonthlyCharges)
        })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Prediction failed');
      
      setResult(data);
      setTimeout(() => {
        document.getElementById('results-panel').scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 100);
    } catch (err) {
      setError(err.message || 'Network error: Make sure backend is running');
    } finally {
      setLoading(false);
    }
  };

  const probPercent = result ? Math.round(result.churn_probability * 100) : 0;
  const isHighRisk = result && result.risk_assessment.includes('High Risk');

  return (
    <>
      <div className="background-orbs">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>
      
      <div className="container">
        <header>
          <h1>Churn<span className="highlight">Predict</span></h1>
          <p>Advanced Customer Retention Intelligence Engine</p>
        </header>

        <div className="main-content">
          <form className="glass-panel" onSubmit={handleSubmit}>
            <div className="form-grid">
              {/* Profile */}
              <div className="form-section">
                <h3><span className="section-icon">👤</span> Profile</h3>
                
                <div className="input-group">
                  <label>Customer ID</label>
                  <input type="text" name="customerID" value={formData.customerID} onChange={handleChange} required />
                </div>
                
                <div className="input-group">
                  <label>Gender</label>
                  <select name="gender" value={formData.gender} onChange={handleChange}>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Senior Citizen</label>
                  <select name="SeniorCitizen" value={formData.SeniorCitizen} onChange={handleChange}>
                    <option value="0">No</option>
                    <option value="1">Yes</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Partner</label>
                  <select name="Partner" value={formData.Partner} onChange={handleChange}>
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Dependents</label>
                  <select name="Dependents" value={formData.Dependents} onChange={handleChange}>
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Tenure (Months)</label>
                  <input type="number" name="tenure" value={formData.tenure} onChange={handleChange} min="0" required />
                </div>
              </div>

              {/* Services */}
              <div className="form-section">
                <h3><span className="section-icon">🌐</span> Services</h3>
                
                <div className="input-group">
                  <label>Phone Service</label>
                  <select name="PhoneService" value={formData.PhoneService} onChange={handleChange}>
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Multiple Lines</label>
                  <select name="MultipleLines" value={formData.MultipleLines} onChange={handleChange}>
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                    <option value="No phone service">No phone service</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Internet Service</label>
                  <select name="InternetService" value={formData.InternetService} onChange={handleChange}>
                    <option value="Fiber optic">Fiber optic</option>
                    <option value="DSL">DSL</option>
                    <option value="No">No</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Online Security</label>
                  <select name="OnlineSecurity" value={formData.OnlineSecurity} onChange={handleChange}>
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                    <option value="No internet service">No internet service</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Online Backup</label>
                  <select name="OnlineBackup" value={formData.OnlineBackup} onChange={handleChange}>
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                    <option value="No internet service">No internet service</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Device Protection</label>
                  <select name="DeviceProtection" value={formData.DeviceProtection} onChange={handleChange}>
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                    <option value="No internet service">No internet service</option>
                  </select>
                </div>
              </div>

              {/* Account & Billing */}
              <div className="form-section">
                <h3><span className="section-icon">💳</span> Account</h3>
                
                <div className="input-group">
                  <label>Tech Support</label>
                  <select name="TechSupport" value={formData.TechSupport} onChange={handleChange}>
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                    <option value="No internet service">No internet service</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Streaming TV</label>
                  <select name="StreamingTV" value={formData.StreamingTV} onChange={handleChange}>
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                    <option value="No internet service">No internet service</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Streaming Movies</label>
                  <select name="StreamingMovies" value={formData.StreamingMovies} onChange={handleChange}>
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                    <option value="No internet service">No internet service</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Contract</label>
                  <select name="Contract" value={formData.Contract} onChange={handleChange}>
                    <option value="Month-to-month">Month-to-month</option>
                    <option value="One year">One year</option>
                    <option value="Two year">Two year</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Paperless Billing</label>
                  <select name="PaperlessBilling" value={formData.PaperlessBilling} onChange={handleChange}>
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Payment Method</label>
                  <select name="PaymentMethod" value={formData.PaymentMethod} onChange={handleChange}>
                    <option value="Electronic check">Electronic check</option>
                    <option value="Mailed check">Mailed check</option>
                    <option value="Bank transfer (automatic)">Bank transfer (automatic)</option>
                    <option value="Credit card (automatic)">Credit card (automatic)</option>
                  </select>
                </div>

                <div className="input-group">
                  <label>Monthly Charges</label>
                  <input type="number" name="MonthlyCharges" value={formData.MonthlyCharges} onChange={handleChange} step="0.01" required />
                </div>

                <div className="input-group">
                  <label>Total Charges</label>
                  <input type="text" name="TotalCharges" value={formData.TotalCharges} onChange={handleChange} required />
                </div>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? <div className="loader"></div> : <span className="btn-text">Analyze Risk</span>}
              </button>
            </div>
            
            {error && <div className="error-msg">{error}</div>}
          </form>

          <div id="results-panel" className={`glass-panel ${!result ? 'results-hidden' : ''}`}>
            <h2>AI Risk Assessment</h2>
            <div className="result-card">
              <div className="score-ring">
                <svg viewBox="0 0 36 36" className="circular-chart">
                  <path className="circle-bg"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path className="circle" 
                    strokeDasharray={`${probPercent}, 100`}
                    style={{ stroke: isHighRisk ? 'var(--danger)' : 'var(--success)' }}
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <text x="18" y="20.35" className="percentage">{probPercent}%</text>
                </svg>
              </div>
              <div className="result-details">
                <h3 style={{ color: isHighRisk ? 'var(--danger)' : 'var(--success)' }}>
                  {isHighRisk ? 'High Churn Risk' : 'Low Churn Risk'}
                </h3>
                <p>
                  {isHighRisk ? 'Immediate retention action required.' : 'Customer is likely to stay.'}
                </p>
                {result && (
                  <div className="threshold-info">
                    Model Threshold: <span>{result.threshold_applied}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
