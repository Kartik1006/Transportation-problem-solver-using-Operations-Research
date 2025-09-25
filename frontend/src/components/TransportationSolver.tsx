import React, { useState, useEffect } from 'react';
import { Play, Download, Settings, AlertCircle, CheckCircle } from 'lucide-react';
import { apiService, TransportationProblem, SolutionResponse, Method } from '../services/api';
import MatrixInput from './MatrixInput';
import SolutionDisplay from './SolutionDisplay';

const TransportationSolver: React.FC = () => {
  // State
  const [methods, setMethods] = useState<Method[]>([]);
  const [problemData, setProblemData] = useState<TransportationProblem>({
    costs: [[8, 6, 10], [9, 12, 13], [14, 7, 16]],
    supply: [100, 150, 125],
    demand: [130, 120, 125],
    method: 'nwcr',
    use_modi: false,
    max_iterations: 10
  });
  const [solution, setSolution] = useState<SolutionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validation, setValidation] = useState<any>(null);

  // Load available methods on component mount
  useEffect(() => {
    const loadMethods = async () => {
      try {
        const methodsData = await apiService.getMethods();
        setMethods(methodsData.transportation_methods);
      } catch (err) {
        console.error('Failed to load methods:', err);
      }
    };
    loadMethods();
  }, []);

  // Validate input when problem data changes
  useEffect(() => {
    const validateInput = async () => {
      try {
        const validationResult = await apiService.validateTransportation(problemData);
        setValidation(validationResult);
      } catch (err) {
        console.error('Validation failed:', err);
      }
    };
    validateInput();
  }, [problemData.costs, problemData.supply, problemData.demand]);

  const handleSolve = async () => {
    setLoading(true);
    setError(null);
    setSolution(null);

    try {
      const result = await apiService.solveTransportation(problemData);
      setSolution(result);
    } catch (err: any) {
      setError(err.message || 'Failed to solve problem');
    } finally {
      setLoading(false);
    }
  };

  const handleMatrixSizeChange = (rows: number, cols: number) => {
    const newCosts = Array(rows).fill(null).map(() => Array(cols).fill(1));
    const newSupply = Array(rows).fill(100);
    const newDemand = Array(cols).fill(100);

    setProblemData(prev => ({
      ...prev,
      costs: newCosts,
      supply: newSupply,
      demand: newDemand
    }));
  };

  const handleExport = () => {
    if (!solution) return;

    const csvData = [
      ['Transportation Problem Results'],
      ['Method', solution.method],
      ['Total Cost', solution.total_cost.toString()],
      [''],
      ['Allocation Matrix'],
      ['', ...Array.from({length: solution.costs[0].length}, (_, i) => `D${i+1}`), 'Supply'],
      ...solution.allocation?.map((row, i) => [
        `S${i+1}`,
        ...row.map(val => val.toString()),
        solution.supply?.[i]?.toString() || ''
      ]) || [],
      ['Demand', ...solution.demand?.map(d => d.toString()) || [], '']
    ];

    const csvContent = csvData.map(row => row.join(',')).join('\\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transportation_solution_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className=\"space-y-8\">
      {/* Problem Setup */}
      <div className=\"bg-white rounded-lg shadow-md p-6\">
        <h2 className=\"text-xl font-semibold text-gray-900 mb-6\">Problem Setup</h2>
        
        {/* Matrix Size Controls */}
        <div className=\"grid grid-cols-2 gap-4 mb-6\">
          <div>
            <label className=\"block text-sm font-medium text-gray-700 mb-2\">
              Sources (Rows)
            </label>
            <select
              value={problemData.costs.length}
              onChange={(e) => handleMatrixSizeChange(parseInt(e.target.value), problemData.costs[0].length)}
              className=\"w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500\"
            >
              {[2, 3, 4, 5, 6].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>
          <div>
            <label className=\"block text-sm font-medium text-gray-700 mb-2\">
              Destinations (Columns)
            </label>
            <select
              value={problemData.costs[0].length}
              onChange={(e) => handleMatrixSizeChange(problemData.costs.length, parseInt(e.target.value))}
              className=\"w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500\"
            >
              {[2, 3, 4, 5, 6].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Cost Matrix */}
        <div className=\"mb-6\">
          <h3 className=\"text-lg font-medium text-gray-900 mb-3\">Cost Matrix</h3>
          <MatrixInput
            matrix={problemData.costs}
            onChange={(newMatrix) => setProblemData(prev => ({ ...prev, costs: newMatrix }))}
            rowLabels={Array.from({length: problemData.costs.length}, (_, i) => `S${i+1}`)}
            colLabels={Array.from({length: problemData.costs[0].length}, (_, i) => `D${i+1}`)}
          />
        </div>

        {/* Supply and Demand */}
        <div className=\"grid grid-cols-1 md:grid-cols-2 gap-6\">
          <div>
            <h3 className=\"text-lg font-medium text-gray-900 mb-3\">Supply</h3>
            <div className=\"space-y-2\">
              {problemData.supply.map((value, index) => (
                <div key={index} className=\"flex items-center space-x-3\">
                  <label className=\"text-sm font-medium text-gray-700 w-12\">S{index + 1}:</label>
                  <input
                    type=\"number\"
                    value={value}
                    onChange={(e) => {
                      const newSupply = [...problemData.supply];
                      newSupply[index] = parseFloat(e.target.value) || 0;
                      setProblemData(prev => ({ ...prev, supply: newSupply }));
                    }}
                    className=\"flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500\"
                    min=\"0\"
                    step=\"0.1\"
                  />
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className=\"text-lg font-medium text-gray-900 mb-3\">Demand</h3>
            <div className=\"space-y-2\">
              {problemData.demand.map((value, index) => (
                <div key={index} className=\"flex items-center space-x-3\">
                  <label className=\"text-sm font-medium text-gray-700 w-12\">D{index + 1}:</label>
                  <input
                    type=\"number\"
                    value={value}
                    onChange={(e) => {
                      const newDemand = [...problemData.demand];
                      newDemand[index] = parseFloat(e.target.value) || 0;
                      setProblemData(prev => ({ ...prev, demand: newDemand }));
                    }}
                    className=\"flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500\"
                    min=\"0\"
                    step=\"0.1\"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Validation Info */}
        {validation && (
          <div className={`mt-4 p-4 rounded-lg flex items-start space-x-3 ${
            validation.valid 
              ? validation.balanced 
                ? 'bg-green-50 text-green-800' 
                : 'bg-yellow-50 text-yellow-800'
              : 'bg-red-50 text-red-800'
          }`}>
            {validation.valid ? (
              validation.balanced ? <CheckCircle className=\"h-5 w-5 mt-0.5 flex-shrink-0\" /> : <AlertCircle className=\"h-5 w-5 mt-0.5 flex-shrink-0\" />
            ) : (
              <AlertCircle className=\"h-5 w-5 mt-0.5 flex-shrink-0\" />
            )}
            <div className=\"text-sm\">
              {validation.valid ? (
                <div>
                  Total Supply: {validation.total_supply}, Total Demand: {validation.total_demand}
                  {!validation.balanced && (
                    <div className=\"mt-1 font-medium\">
                      ⚠️ Unbalanced problem - dummy source/destination will be added automatically
                    </div>
                  )}
                </div>
              ) : (
                <div className=\"font-medium\">{validation.error}</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Method Selection */}
      <div className=\"bg-white rounded-lg shadow-md p-6\">
        <h2 className=\"text-xl font-semibold text-gray-900 mb-6 flex items-center space-x-2\">
          <Settings className=\"h-5 w-5\" />
          <span>Solution Method</span>
        </h2>

        <div className=\"grid grid-cols-1 md:grid-cols-2 gap-6\">
          <div>
            <label className=\"block text-sm font-medium text-gray-700 mb-2\">
              Algorithm
            </label>
            <select
              value={problemData.method}
              onChange={(e) => setProblemData(prev => ({ ...prev, method: e.target.value as any }))}
              className=\"w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500\"
            >
              {methods.map((method) => (
                <option key={method.key} value={method.key}>
                  {method.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className=\"flex items-center space-x-3\">
              <input
                type=\"checkbox\"
                checked={problemData.use_modi}
                onChange={(e) => setProblemData(prev => ({ ...prev, use_modi: e.target.checked }))}
                className=\"h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded\"
              />
              <span className=\"text-sm font-medium text-gray-700\">Apply MODI Optimization</span>
            </label>
            {problemData.use_modi && (
              <div className=\"mt-3\">
                <label className=\"block text-sm font-medium text-gray-700 mb-1\">
                  Max Iterations
                </label>
                <input
                  type=\"number\"
                  value={problemData.max_iterations}
                  onChange={(e) => setProblemData(prev => ({ ...prev, max_iterations: parseInt(e.target.value) || 10 }))}
                  className=\"w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500\"
                  min=\"1\"
                  max=\"50\"
                />
              </div>
            )}
          </div>
        </div>

        <div className=\"flex items-center space-x-4 mt-6\">
          <button
            onClick={handleSolve}
            disabled={loading || !validation?.valid}
            className=\"flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors\"
          >
            <Play className=\"h-4 w-4\" />
            <span>{loading ? 'Solving...' : 'Solve Problem'}</span>
          </button>

          {solution && (
            <button
              onClick={handleExport}
              className=\"flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors\"
            >
              <Download className=\"h-4 w-4\" />
              <span>Export CSV</span>
            </button>
          )}
        </div>

        {error && (
          <div className=\"mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm\">
            {error}
          </div>
        )}
      </div>

      {/* Solution Display */}
      {solution && (
        <SolutionDisplay solution={solution} problemType=\"transportation\" />
      )}
    </div>
  );
};

export default TransportationSolver;
