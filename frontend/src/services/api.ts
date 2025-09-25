import axios from 'axios';

// Configure base URL - change this to your deployed backend URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface TransportationProblem {
  costs: number[][];
  supply: number[];
  demand: number[];
  method: 'nwcr' | 'least_cost' | 'vam' | 'row_minima';
  use_modi?: boolean;
  max_iterations?: number;
}

export interface AssignmentProblem {
  costs: number[][];
}

export interface SolutionResponse {
  method: string;
  allocation?: number[][];
  assignment?: number[][];
  total_cost: number;
  steps: any[];
  costs: number[][];
  supply?: number[];
  demand?: number[];
  dummy_added?: any;
  converged?: boolean;
  iterations?: number;
}

export interface ValidationResponse {
  valid: boolean;
  total_supply?: number;
  total_demand?: number;
  balanced?: boolean;
  matrix_size?: number[];
  error?: string;
}

export interface Method {
  key: string;
  name: string;
}

export interface MethodsResponse {
  transportation_methods: Method[];
  assignment_methods: Method[];
  optimization_methods: Method[];
}

// API functions
export const apiService = {
  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await api.get('/health');
    return response.data;
  },

  // Get available methods
  async getMethods(): Promise<MethodsResponse> {
    const response = await api.get('/methods');
    return response.data;
  },

  // Solve transportation problem
  async solveTransportation(problem: TransportationProblem): Promise<SolutionResponse> {
    const response = await api.post('/solve/transportation', problem);
    return response.data;
  },

  // Solve assignment problem
  async solveAssignment(problem: AssignmentProblem): Promise<SolutionResponse> {
    const response = await api.post('/solve/assignment', problem);
    return response.data;
  },

  // Validate transportation input
  async validateTransportation(problem: TransportationProblem): Promise<ValidationResponse> {
    const response = await api.post('/validate/transportation', problem);
    return response.data;
  },

  // Validate assignment input
  async validateAssignment(problem: AssignmentProblem): Promise<ValidationResponse> {
    const response = await api.post('/validate/assignment', problem);
    return response.data;
  },

  // Apply MODI optimization
  async optimizeWithModi(
    allocation: number[][], 
    costs: number[][], 
    maxIterations: number = 10
  ): Promise<any> {
    const response = await api.post('/optimize/modi', {
      allocation,
      costs,
      max_iterations: maxIterations
    });
    return response.data;
  }
};

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
      throw new Error(error.response.data.detail || 'An error occurred');
    } else if (error.request) {
      // Request was made but no response
      console.error('Network Error:', error.request);
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      console.error('Error:', error.message);
      throw new Error(error.message);
    }
  }
);
