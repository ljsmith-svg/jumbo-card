import React, { useState } from 'react';
import { 
  CardFormData, 
  CharacterTheme,
  CardStyle, 
  CardSize, 
  ColorTheme 
} from './types';
import { generateChristmasCard } from './services/geminiService';
import { Spinner } from './components/Spinner';

// Pre-defined lists for dropdowns
const CHARACTER_THEMES = Object.values(CharacterTheme);
const STYLES = Object.values(CardStyle);
const SIZES = Object.values(CardSize);
const COLORS = Object.values(ColorTheme);

const App: React.FC = () => {
  const [formData, setFormData] = useState<CardFormData>({
    childName: '',
    toName: '',
    fromName: '',
    characterTheme: CharacterTheme.ELMO, // Default to a Sesame character
    cardStyle: CardStyle.CARTOON,
    cardSize: CardSize.SIZE_8_5_11,
    colorTheme: ColorTheme.RED_GREEN,
  });

  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.childName.trim()) {
      setError("Please enter a child's name!");
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedImage(null);

    try {
      const imageUrl = await generateChristmasCard(formData);
      setGeneratedImage(imageUrl);
    } catch (err) {
      setError("Failed to generate card. Please try again. " + (err instanceof Error ? err.message : ''));
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!generatedImage) return;
    const link = document.createElement('a');
    link.href = generatedImage;
    
    // Create a clean filename
    const safeChildName = formData.childName.trim().replace(/[^a-z0-9]/gi, '_');
    const safeTheme = formData.characterTheme.replace(/[^a-z0-9]/gi, '_');
    const timestamp = new Date().toISOString().split('T')[0];
    
    link.download = `ChristmasCard-${safeChildName}-${safeTheme}-${timestamp}-300dpi.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Brand Colors for Inline Styles
  const brandRed = '#D92E43';
  const brandGold = '#F4C85C';
  const brandGreen = '#0B3F2E';

  return (
    <div className="min-h-screen flex flex-col bg-red-50 relative overflow-hidden font-sans text-slate-800">
      {/* Decorative Background Elements */}
      <div className="absolute inset-0 pointer-events-none snow-bg opacity-50"></div>
      
      {/* Header */}
      <header className="relative z-10 bg-white/90 backdrop-blur-md shadow-sm border-b border-red-100 sticky top-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-3xl">🎄</span>
            <h1 className="text-3xl font-bold festive-font tracking-wider" style={{ color: brandRed }}>
              Holiday Jumbo Card
            </h1>
          </div>
          <div className="hidden sm:block font-semibold text-sm" style={{ color: brandGreen }}>
            Powered by Imagen 4
          </div>
        </div>
      </header>

      <main className="flex-grow relative z-10 container mx-auto px-4 py-8 sm:py-12">
        <div className="flex flex-col lg:flex-row gap-8 xl:gap-12">
          
          {/* LEFT: Form Configuration */}
          <div className="w-full lg:w-1/3 flex-shrink-0">
            <div className="bg-white rounded-2xl shadow-xl border border-red-100 p-6 sm:p-8">
              <h2 className="text-2xl text-gray-800 font-bold mb-6 festive-font flex items-center gap-2">
                <span style={{ color: brandRed }}>❄️</span> Customize Your Card
              </h2>
              
              <form onSubmit={handleGenerate} className="space-y-5">
                
                {/* Child's Name */}
                <div>
                  <label htmlFor="childName" className="block text-sm font-bold text-gray-700 mb-1">
                    Child's Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="childName"
                    name="childName"
                    value={formData.childName}
                    onChange={handleInputChange}
                    className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 border p-2.5 transition-colors"
                    style={{ borderColor: brandGold }}
                    placeholder="e.g. Timmy"
                    required
                  />
                </div>

                {/* To / From */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="toName" className="block text-sm font-bold text-gray-700 mb-1">
                      To (Optional)
                    </label>
                    <input
                      type="text"
                      id="toName"
                      name="toName"
                      value={formData.toName}
                      onChange={handleInputChange}
                      className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 border p-2.5"
                      placeholder="Grandma"
                    />
                  </div>
                  <div>
                    <label htmlFor="fromName" className="block text-sm font-bold text-gray-700 mb-1">
                      From (Optional)
                    </label>
                    <input
                      type="text"
                      id="fromName"
                      name="fromName"
                      value={formData.fromName}
                      onChange={handleInputChange}
                      className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 border p-2.5"
                      placeholder="Santa"
                    />
                  </div>
                </div>

                {/* Character Theme */}
                <div>
                  <label htmlFor="characterTheme" className="block text-sm font-bold text-gray-700 mb-1">
                    Character Theme
                  </label>
                  <select
                    id="characterTheme"
                    name="characterTheme"
                    value={formData.characterTheme}
                    onChange={handleInputChange}
                    className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 border p-2.5 bg-white"
                  >
                    {CHARACTER_THEMES.map(theme => (
                      <option key={theme} value={theme}>{theme}</option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">Background will automatically match your character!</p>
                </div>

                {/* Style & Size */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="cardStyle" className="block text-sm font-bold text-gray-700 mb-1">
                      Style
                    </label>
                    <select
                      id="cardStyle"
                      name="cardStyle"
                      value={formData.cardStyle}
                      onChange={handleInputChange}
                      className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 border p-2.5 bg-white"
                    >
                      {STYLES.map(s => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="cardSize" className="block text-sm font-bold text-gray-700 mb-1">
                      Paper Size
                    </label>
                    <select
                      id="cardSize"
                      name="cardSize"
                      value={formData.cardSize}
                      onChange={handleInputChange}
                      className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 border p-2.5 bg-white"
                    >
                      {SIZES.map(s => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Color Theme */}
                <div>
                  <label htmlFor="colorTheme" className="block text-sm font-bold text-gray-700 mb-1">
                    Color Theme
                  </label>
                  <select
                    id="colorTheme"
                    name="colorTheme"
                    value={formData.colorTheme}
                    onChange={handleInputChange}
                    className="block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 border p-2.5 bg-white"
                  >
                    {COLORS.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-200 flex items-center gap-2">
                    <span>⚠️</span> {error}
                  </div>
                )}

                {/* Action Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full py-4 px-6 rounded-xl text-white font-bold text-lg shadow-lg transition-all transform hover:scale-[1.02] active:scale-95 ${
                    loading 
                      ? 'bg-gray-400 cursor-not-allowed' 
                      : 'shadow-red-300/50'
                  }`}
                  style={{ 
                    backgroundColor: loading ? undefined : brandRed 
                  }}
                >
                  {loading ? 'Creating Magic...' : '✨ Create Card'}
                </button>
              </form>
            </div>
          </div>

          {/* RIGHT: Preview Area */}
          <div className="w-full lg:w-2/3 flex flex-col">
            <div className="flex-grow bg-white/50 backdrop-blur-sm border-4 border-dashed rounded-3xl flex items-center justify-center p-4 min-h-[500px] relative shadow-inner transition-all"
                 style={{ borderColor: brandRed + '40' }}>
              
              {loading ? (
                <Spinner />
              ) : generatedImage ? (
                <div className="relative group w-full h-full flex items-center justify-center">
                  <img
                    src={generatedImage}
                    alt="Generated Christmas Card"
                    className="max-w-full max-h-[75vh] rounded-lg shadow-2xl border-8 border-white object-contain"
                  />
                  <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/50 text-white px-3 py-1 rounded-full text-sm pointer-events-none">
                    Preview
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-400 max-w-md p-6">
                  <div className="text-7xl mb-6 opacity-40 animate-bounce delay-1000">🎁</div>
                  <h3 className="text-2xl font-bold mb-3 text-gray-500 festive-font">No Card Created Yet</h3>
                  <p className="text-lg">Fill out the form on the left and click "Create Card" to see your holiday masterpiece appear here!</p>
                </div>
              )}
            </div>

            {/* Download Action */}
            {generatedImage && !loading && (
              <div className="mt-6 flex justify-center animate-fade-in-up">
                <button
                  onClick={handleDownload}
                  className="flex items-center space-x-2 text-white font-bold py-3 px-8 rounded-full shadow-lg transform transition-all hover:scale-105 active:scale-95"
                  style={{ backgroundColor: brandGreen, boxShadow: `0 4px 14px ${brandGreen}66` }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  <span>Download Printable JPG</span>
                </button>
              </div>
            )}
          </div>

        </div>
      </main>

      {/* Footer with Brand Community Link */}
      <footer className="bg-white/80 backdrop-blur border-t border-red-100 py-6 mt-auto relative z-10">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm font-semibold mb-2" style={{ color: brandGreen }}>
            Created by Just Lois
          </p>
          <a 
            href="https://www.facebook.com/share/g/1BNRxzNyac/?mibextid=wwXIfr" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-xs hover:underline transition-colors inline-flex items-center gap-1"
            style={{ color: brandRed }}
          >
            <span>Join the Sista'a & Brotha's Craft N' Creation Community</span>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </footer>
    </div>
  );
};

export default App;