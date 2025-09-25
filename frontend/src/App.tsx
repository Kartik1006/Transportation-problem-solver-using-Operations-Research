import React, { useState } from 'react';
import { Truck, Calculator, Info, Github } from 'lucide-react';
import TransportationSolver from './components/TransportationSolver';
import AssignmentSolver from './components/AssignmentSolver';

type ProblemType = 'transportation' | 'assignment';

function App() {
  const [currentProblem, setCurrentProblem] = useState<ProblemType>('transportation');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-500 p-2 rounded-lg">
                <Truck className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Transportation Problem Solver
                </h1>
                <p className="text-gray-600 mt-1">
                  Solve optimization problems with step-by-step solutions
                </p>
              </div>
            </div>
            <a 
              href="https://github.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <Github className="h-6 w-6" />
            </a>
          </div>
        </div>
      </header>

      {/* Problem Type Selector */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Problem Type</h2>
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={() => setCurrentProblem('transportation')}
              className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all ${
                currentProblem === 'transportation'
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 hover:border-gray-300 text-gray-700'
              }`}
            >
              <Truck className="h-6 w-6" />
              <div className="text-left">
                <div className="font-medium">Transportation Problem</div>
                <div className="text-sm opacity-75">
                  Optimize supply-demand distribution
                </div>
              </div>
            </button>
            
            <button
              onClick={() => setCurrentProblem('assignment')}
              className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all ${
                currentProblem === 'assignment'
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 hover:border-gray-300 text-gray-700'
              }`}
            >
              <Calculator className="h-6 w-6" />
              <div className="text-left">
                <div className="font-medium">Assignment Problem</div>
                <div className="text-sm opacity-75">
                  One-to-one optimal matching
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Problem Solver */}
        {currentProblem === 'transportation' ? (
          <TransportationSolver />
        ) : (
          <AssignmentSolver />
        )}

        {/* Info Panel */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <div className="flex items-start space-x-3">
            <Info className="h-6 w-6 text-blue-500 mt-0.5 flex-shrink-0" />
            <div className="text-gray-700">
              <h3 className="font-medium text-gray-900 mb-2">How to Use</h3>
              <ul className="space-y-1 text-sm">
                <li>• <strong>Transportation:</strong> Enter costs, supply, and demand. Choose a method and optionally enable MODI optimization.</li>
                <li>• <strong>Assignment:</strong> Enter a square cost matrix for one-to-one assignments using the Hungarian algorithm.</li>
                <li>• View detailed step-by-step solutions and export results as needed.</li>
                <li>• All algorithms handle balancing and optimization automatically.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-gray-300">
              Built with React, TypeScript, Tailwind CSS, and FastAPI
            </p>
            <p className="text-gray-400 text-sm mt-2">
              Algorithms: NWCR, Least Cost, VAM, Hungarian, MODI
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
