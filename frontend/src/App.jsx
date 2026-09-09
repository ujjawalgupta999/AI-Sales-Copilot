import { useState } from 'react';

function App() {
  const [prospectName, setProspectName] = useState('');
  const [company, setCompany] = useState('');
  const [emailOutput, setEmailOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(emailOutput);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setEmailOutput('');

    try {
      const response = await fetch('http://127.0.0.1:8000/generate-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prospect_name: prospectName,
          company: company
        }),
      });

      const data = await response.json();
      setEmailOutput(data.email);
    } catch (error) {
      setEmailOutput('Error connecting to the AI agent.');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '50px auto', fontFamily: 'system-ui' }}>
      <h2>AI Sales Copilot</h2>
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <input 
          type="text" 
          placeholder="Prospect Name (e.g., Tim Cook)" 
          value={prospectName} 
          onChange={(e) => setProspectName(e.target.value)} 
          required 
          style={{ padding: '10px', fontSize: '16px' }}
        />
        <input 
          type="text" 
          placeholder="Company (e.g., Apple)" 
          value={company} 
          onChange={(e) => setCompany(e.target.value)} 
          required 
          style={{ padding: '10px', fontSize: '16px' }}
        />
        <button 
          type="submit" 
          disabled={isLoading}
          style={{ padding: '10px', fontSize: '16px', cursor: 'pointer' }}
        >
          {isLoading ? 'Generating Draft...' : 'Draft Email'}
        </button>
      </form>

     {emailOutput && (
        <div style={{ marginTop: '30px', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', whiteSpace: 'pre-wrap', position: 'relative' }}>
          <strong>Generated Draft:</strong>
          
          <button 
            onClick={handleCopy}
            style={{ position: 'absolute', top: '10px', right: '10px', padding: '5px 10px', cursor: 'pointer' }}
          >
            {isCopied ? 'Copied!' : 'Copy to Clipboard'}
          </button>

          <p>{emailOutput}</p>
        </div>
      )}
    </div>
  );
}

export default App;