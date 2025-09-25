import React from 'react';

interface MatrixInputProps {
  matrix: number[][];
  onChange: (matrix: number[][]) => void;
  rowLabels?: string[];
  colLabels?: string[];
}

const MatrixInput: React.FC<MatrixInputProps> = ({ matrix, onChange, rowLabels, colLabels }) => {
  const handleCellChange = (row: number, col: number, value: string) => {
    const newMatrix = matrix.map((r, i) => 
      i === row ? r.map((c, j) => j === col ? parseFloat(value) || 0 : c) : r
    );
    onChange(newMatrix);
  };

  return (
    <div className="overflow-x-auto">
      <table className="border-collapse border border-gray-300">
        {colLabels && (
          <thead>
            <tr>
              <th className="border border-gray-300 p-2 bg-gray-50"></th>
              {colLabels.map((label, index) => (
                <th key={index} className="border border-gray-300 p-2 bg-gray-50 font-medium text-sm">
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
                <th className="border border-gray-300 p-2 bg-gray-50 font-medium text-sm">
                  {rowLabels[rowIndex]}
                </th>
              )}
              {row.map((cell, colIndex) => (
                <td key={colIndex} className="border border-gray-300 p-1">
                  <input
                    type="number"
                    value={cell}
                    onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
                    className="w-16 px-2 py-1 text-center border-0 focus:ring-2 focus:ring-primary-500 rounded"
                    step="0.1"
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MatrixInput;
