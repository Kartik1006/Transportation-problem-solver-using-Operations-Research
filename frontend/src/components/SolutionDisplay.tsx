import React, { useState } from 'react';
import { ChevronDown, ChevronRight, BarChart3, Target } from 'lucide-react';
import { SolutionResponse } from '../services/api';

interface SolutionDisplayProps {
  solution: SolutionResponse;
  problemType: 'transportation' | 'assignment';
}

const SolutionDisplay: React.FC<SolutionDisplayProps> = ({ solution, problemType }) => {
  const [expandedSteps, setExpandedSteps] = useState<boolean>(false);

  const formatMatrix = (matrix: number[][], rowLabels?: string[], colLabels?: string[]) => (
    <div className="overflow-x-auto">
      <table className="border-collapse border border-gray-300 text-sm">
        {colLabels && (
          <thead>
            <tr>
              <th className="border border-gray-300 p-2 bg-gray-50"></th>
              {colLabels.map((label, index) => (
                <th key={index} className="border border-gray-300 p-2 bg-gray-50 font-medium">
                  {label}
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {matrix.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {rowLabels && (
                <th className="border border-gray-300 p-2 bg-gray-50 font-medium">
                  {rowLabels[rowIndex]}
                </th>
              )}
              {row.map((cell, colIndex) => (
                <td key={colIndex} className="border border-gray-300 p-2 text-center">
                  {cell.toFixed(1)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center space-x-2">
        <Target className="h-5 w-5" />
        <span>Solution Results</span>
      </h2>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-primary-50 rounded-lg p-4">
          <div className="text-sm text-primary-600 font-medium">Method</div>
          <div className="text-lg font-semibold text-primary-900">{solution.method}</div>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4">
          <div className="text-sm text-green-600 font-medium">Total Cost</div>
          <div className="text-lg font-semibold text-green-900">{solution.total_cost.toFixed(2)}</div>
        </div>
        
        {solution.iterations !== undefined && (
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-sm text-blue-600 font-medium">Iterations</div>
            <div className="text-lg font-semibold text-blue-900">{solution.iterations}</div>
          </div>
        )}
      </div>

      {/* Final Solution */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {problemType === 'assignment' ? 'Optimal Assignments' : 'Final Allocation'}
        </h3>
        
        {problemType === 'assignment' ? (
          <div className="space-y-3">
            {solution.assignment?.map((pair: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">Worker {pair[0] + 1} → Job {pair[1] + 1}</span>
                <span className="text-green-600 font-semibold">
                  Cost: {solution.costs[pair[0]][pair[1]]}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div>
            {solution.allocation && formatMatrix(
              solution.allocation,
              Array.from({length: solution.allocation.length}, (_, i) => `S${i+1}`),
              Array.from({length: solution.allocation[0].length}, (_, i) => `D${i+1}`)
            )}
            
            {/* Supply and Demand Check */}
            {solution.supply && solution.demand && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Supply Verification</h4>
                  <div className="space-y-1 text-sm">
                    {solution.supply.map((supply, index) => (
                      <div key={index} className="flex justify-between">
                        <span>S{index + 1}:</span>
                        <span>{supply.toFixed(1)} / {solution.allocation![index].reduce((sum, val) => sum + val, 0).toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Demand Verification</h4>
                  <div className="space-y-1 text-sm">
                    {solution.demand.map((demand, index) => (
                      <div key={index} className="flex justify-between">
                        <span>D{index + 1}:</span>
                        <span>{demand.toFixed(1)} / {solution.allocation!.reduce((sum, row) => sum + row[index], 0).toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Step-by-Step Solution */}
      <div>
        <button
          onClick={() => setExpandedSteps(!expandedSteps)}
          className="flex items-center space-x-2 text-lg font-semibold text-gray-900 hover:text-primary-600 transition-colors mb-4"
        >
          {expandedSteps ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
          <BarChart3 className="h-5 w-5" />
          <span>Step-by-Step Solution ({solution.steps.length} steps)</span>
        </button>

        {expandedSteps && (
          <div className="space-y-4 border-l-4 border-primary-200 pl-6">
            {solution.steps.map((step, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-start space-x-3 mb-3">
                  <div className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium">
                    {step.step}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{step.description}</p>
                  </div>
                </div>
                
                {step.allocation && (
                  <div className="mt-3">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Current Allocation:</h5>
                    {formatMatrix(
                      step.allocation,
                      Array.from({length: step.allocation.length}, (_, i) => `S${i+1}`),
                      Array.from({length: step.allocation[0].length}, (_, i) => `D${i+1}`)
                    )}
                  </div>
                )}
                
                {step.costs && problemType === 'assignment' && (
                  <div className="mt-3">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Matrix State:</h5>
                    {formatMatrix(
                      step.costs,
                      Array.from({length: step.costs.length}, (_, i) => `R${i+1}`),
                      Array.from({length: step.costs[0].length}, (_, i) => `C${i+1}`)
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SolutionDisplay;
