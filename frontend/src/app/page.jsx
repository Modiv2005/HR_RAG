import AdminUpload from '../components/AdminUpload';
import ChatInterface from '../components/ChatInterface';

export const metadata = {
  title: 'AI HR Policy Assistant',
  description: 'Strict, document-grounded HR assistant answering employee queries based on uploaded policies.',
};

export default function Home() {
  return (
    <div className="app-container">
      <header className="header">
        <h1>AI HR Assistant</h1>
        <p>Ask questions securely and accurately based ONLY on company policy documents.</p>
      </header>
      
      <main className="grid-layout">
        {/* Left Column: Admin Section */}
        <div>
          <AdminUpload />
        </div>
        
        {/* Right Column: Employee Chat Section */}
        <div>
          <ChatInterface />
        </div>
      </main>
    </div>
  );
}
