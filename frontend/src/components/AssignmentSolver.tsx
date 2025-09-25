import React, { useState } from 'react';
import { Play, Download, AlertCircle } from 'lucide-react';
import { apiService, AssignmentProblem, SolutionResponse } from '../services/api';
import MatrixInput from './MatrixInput';
import SolutionDisplay from './SolutionDisplay';

const AssignmentSolver: React.FC = () => {
  const [problemData, setProblemData] = useState<AssignmentProblem>({
    costs: [[9, 2, 7], [6, 4, 3], [5, 8, 1]]
  });
  const [solution, setSolution] = useState<SolutionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSolve = async () => {
    setLoading(true);
    setError(null);
    setSolution(null);

    try {
      const result = await apiService.solveAssignment(problemData);
      setSolution(result);
    } catch (err: any) {
      setError(err.message || 'Failed to solve problem');
    } finally {
      setLoading(false);
    }
  };

  const handleMatrixSizeChange = (size: number) => {
    const newMatrix = Array(size).fill(null).map(() => Array(size).fill(1));
    setProblemData({ costs: newMatrix });
  };

  const handleExport = () => {
    if (!solution) return;

    const csvData = [
      ['Assignment Problem Results'],
      ['Method', solution.method],
      ['Total Cost', solution.total_cost.toString()],
      [''],
      ['Assignments'],
      ['Worker', 'Job', 'Cost'],
      ...(solution.assignment?.map((pair: any, i: number) => [
        `Worker ${pair[0] + 1}`,
        `Job ${pair[1] + 1}`,
        solution.costs[pair[0]][pair[1]].toString()
      ]) || [])
    ];

    const csvContent = csvData.map(row => row.join(',')).join('\\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `assignment_solution_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      {/* Problem Setup */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Assignment Problem Setup</h2>
        
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Matrix Size (n×n)
          </label>
          <select
            value={problemData.costs.length}
            onChange={(e) => handleMatrixSizeChange(parseInt(e.target.value))}
            className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            {[2, 3, 4, 5, 6].map(num => (
              <option key={num} value={num}>{num}×{num}</option>
            ))}
          </select>
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Cost Matrix</h3>
          <MatrixInput
            matrix={problemData.costs}
            onChange={(newMatrix) => setProblemData({ costs: newMatrix })}
            rowLabels={Array.from({length: problemData.costs.length}, (_, i) => `W${i+1}`)}
            colLabels={Array.from({length: problemData.costs[0].length}, (_, i) => `J${i+1}`)}
          />
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Assignment Problem</p>
              <p>Each worker is assigned to exactly one job for optimal total cost minimization using the Hungarian Algorithm.</p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={handleSolve}
            disabled={loading}
            className="flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <Play className="h-4 w-4" />
            <span>{loading ? 'Solving...' : 'Solve Assignment'}</span>
          </button>

          {solution && (
            <button
              onClick={handleExport}
              className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Download className="h-4 w-4" />
              <span>Export CSV</span>
            </button>
          )}
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Solution Display */}
      {solution && (
        <SolutionDisplay solution={solution} problemType="assignment" />
      )}
    </div>
  );
};

export default AssignmentSolver;
