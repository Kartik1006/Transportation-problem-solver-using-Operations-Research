import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import csv

from transport import (
    nwcr, least_cost, vam, row_minima, assignment_hungarian, 
    modi_improvement, format_allocation_table
)


def main():
    st.title("🚛 Transportation Problem Solver")
    st.markdown("Solve transportation and assignment problems using various methods with step-by-step solutions.")

    # Sidebar for method selection and options
    st.sidebar.header("Method Selection")
    
    problem_type = st.sidebar.selectbox(
        "Problem Type:",
        ["Transportation Problem", "Assignment Problem"]
    )
    
    if problem_type == "Transportation Problem":
        method = st.sidebar.selectbox(
            "Choose Method:",
            ["NWCR", "Least Cost", "VAM", "Row Minima"]
        )
        use_modi = st.sidebar.checkbox("Apply MODI Optimization", value=False)
        if use_modi:
            max_iterations = st.sidebar.slider("MODI Max Iterations:", 1, 20, 10)
    else:
        method = "Hungarian Algorithm"
        use_modi = False

    st.sidebar.header("Problem Setup")

    # Problem input section
    if problem_type == "Transportation Problem":
        st.header("Problem Input")
        
        # Matrix size selection
        col1, col2 = st.columns(2)
        with col1:
            m = st.number_input("Number of Sources (rows):", min_value=2, max_value=10, value=3)
        with col2:
            n = st.number_input("Number of Destinations (columns):", min_value=2, max_value=10, value=3)

        # Initialize session state for matrices
        if 'cost_matrix' not in st.session_state or st.session_state.cost_matrix.shape != (m, n):
            st.session_state.cost_matrix = np.ones((m, n), dtype=float)
        if 'supply' not in st.session_state or len(st.session_state.supply) != m:
            st.session_state.supply = np.ones(m, dtype=float) * 100
        if 'demand' not in st.session_state or len(st.session_state.demand) != n:
            st.session_state.demand = np.ones(n, dtype=float) * 100

        st.subheader("Cost Matrix")
        
        # Create editable cost matrix
        cost_df = pd.DataFrame(
            st.session_state.cost_matrix,
            index=[f"S{i+1}" for i in range(m)],
            columns=[f"D{j+1}" for j in range(n)]
        )
        
        edited_cost = st.data_editor(cost_df, use_container_width=True)
        st.session_state.cost_matrix = edited_cost.values.astype(float)

        # Supply and demand input
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Supply")
            supply_df = pd.DataFrame({
                'Source': [f"S{i+1}" for i in range(m)],
                'Supply': st.session_state.supply
            })
            edited_supply = st.data_editor(supply_df, use_container_width=True, hide_index=True)
            st.session_state.supply = edited_supply['Supply'].values.astype(float)

        with col2:
            st.subheader("Demand")
            demand_df = pd.DataFrame({
                'Destination': [f"D{j+1}" for j in range(n)],
                'Demand': st.session_state.demand
            })
            edited_demand = st.data_editor(demand_df, use_container_width=True, hide_index=True)
            st.session_state.demand = edited_demand['Demand'].values.astype(float)

        # Display supply/demand balance info
        total_supply = np.sum(st.session_state.supply)
        total_demand = np.sum(st.session_state.demand)
        st.info(f"Total Supply: {total_supply}, Total Demand: {total_demand}")
        
        if abs(total_supply - total_demand) > 1e-6:
            st.warning("Unbalanced problem! Dummy source/destination will be added automatically.")

    else:  # Assignment Problem
        st.header("Assignment Problem Input")
        st.info("In assignment problems, each source is assigned to exactly one destination (one-to-one matching).")
        
        # Matrix size selection
        n = st.number_input("Matrix Size (n×n):", min_value=2, max_value=10, value=3)
        
        # Initialize session state for assignment matrix
        if 'assign_matrix' not in st.session_state or st.session_state.assign_matrix.shape != (n, n):
            st.session_state.assign_matrix = np.random.randint(1, 20, (n, n)).astype(float)

        st.subheader("Cost Matrix")
        
        # Create editable cost matrix
        assign_df = pd.DataFrame(
            st.session_state.assign_matrix,
            index=[f"Worker {i+1}" for i in range(n)],
            columns=[f"Job {j+1}" for j in range(n)]
        )
        
        edited_assign = st.data_editor(assign_df, use_container_width=True)
        st.session_state.assign_matrix = edited_assign.values.astype(float)

    # Solve button
    if st.button("🚀 Solve Problem", type="primary"):
        try:
            with st.spinner("Solving..."):
                if problem_type == "Transportation Problem":
                    costs = st.session_state.cost_matrix
                    supply = st.session_state.supply
                    demand = st.session_state.demand
                    
                    # Choose method
                    if method == "NWCR":
                        result = nwcr(costs, supply, demand)
                    elif method == "Least Cost":
                        result = least_cost(costs, supply, demand)
                    elif method == "VAM":
                        result = vam(costs, supply, demand)
                    elif method == "Row Minima":
                        result = row_minima(costs, supply, demand)
                    
                    # Store initial result
                    st.session_state.initial_result = result
                    
                    # Apply MODI if requested
                    if use_modi:
                        modi_result = modi_improvement(result['allocation'], result['costs'], max_iterations)
                        st.session_state.final_result = modi_result
                        st.session_state.used_modi = True
                    else:
                        st.session_state.final_result = result
                        st.session_state.used_modi = False
                        
                else:  # Assignment Problem
                    costs = st.session_state.assign_matrix
                    result = assignment_hungarian(costs)
                    st.session_state.initial_result = result
                    st.session_state.final_result = result
                    st.session_state.used_modi = False

                st.success("Problem solved successfully!")
                
        except Exception as e:
            st.error(f"Error solving problem: {str(e)}")

    # Display results
    if 'final_result' in st.session_state:
        display_results(st.session_state.initial_result, st.session_state.final_result, st.session_state.used_modi, problem_type)


def display_results(initial_result, final_result, used_modi, problem_type):
    """Display the solution results with step-by-step breakdown."""
    
    st.header("📊 Solution Results")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Method", initial_result['method'])
    
    with col2:
        if used_modi:
            improvement = initial_result['total_cost'] - final_result['total_cost']
            st.metric("Initial Cost", f"{initial_result['total_cost']:.2f}")
        else:
            st.metric("Total Cost", f"{final_result['total_cost']:.2f}")
    
    with col3:
        if used_modi:
            st.metric("Final Cost (after MODI)", f"{final_result['total_cost']:.2f}", 
                     delta=f"-{improvement:.2f}")
        elif problem_type == "Assignment Problem":
            st.metric("Assignments", len(final_result['assignment']))

    # Display final solution
    st.subheader("Final Solution")
    
    if problem_type == "Assignment Problem":
        # Display assignment pairs
        assign_df = pd.DataFrame([
            {"Worker": f"Worker {i+1}", "Job": f"Job {j+1}", "Cost": final_result['costs'][i, j]}
            for i, j in final_result['assignment']
        ])
        st.dataframe(assign_df, use_container_width=True)
        
    else:
        # Display allocation table
        if 'allocation' in final_result:
            allocation = final_result['allocation']
            costs = final_result['costs']
            
            # Create formatted table
            display_table = format_allocation_table(allocation, costs)
            st.dataframe(display_table, use_container_width=True)
            
            # Add supply and demand totals
            col1, col2 = st.columns(2)
            with col1:
                if 'supply' in final_result:
                    supply_df = pd.DataFrame({
                        'Source': [f"S{i+1}" for i in range(len(final_result['supply']))],
                        'Supply': final_result['supply'],
                        'Allocated': allocation.sum(axis=1)
                    })
                    st.subheader("Supply Check")
                    st.dataframe(supply_df, use_container_width=True)
            
            with col2:
                if 'demand' in final_result:
                    demand_df = pd.DataFrame({
                        'Destination': [f"D{j+1}" for j in range(len(final_result['demand']))],
                        'Demand': final_result['demand'],
                        'Allocated': allocation.sum(axis=0)
                    })
                    st.subheader("Demand Check")
                    st.dataframe(demand_df, use_container_width=True)

    # Step-by-step solution
    display_steps(initial_result, final_result, used_modi, problem_type)
    
    # Export functionality
    add_export_functionality(final_result, problem_type)


def display_steps(initial_result, final_result, used_modi, problem_type):
    """Display step-by-step solution process."""
    
    st.subheader("📋 Step-by-Step Solution")
    
    # Initial method steps
    with st.expander(f"**{initial_result['method']} Steps**", expanded=True):
        display_method_steps(initial_result, problem_type)
    
    # MODI steps if used
    if used_modi and 'steps' in final_result:
        with st.expander("**MODI Optimization Steps**", expanded=False):
            display_method_steps(final_result, "Transportation Problem")


def display_method_steps(result, problem_type):
    """Display the steps for a specific method."""
    
    if problem_type == "Assignment Problem":
        # For Hungarian algorithm, show the matrix transformations
        for i, step in enumerate(result['steps']):
            st.write(f"**Step {step['step']}:** {step['description']}")
            if 'costs' in step:
                step_df = pd.DataFrame(
                    step['costs'],
                    index=[f"R{i+1}" for i in range(step['costs'].shape[0])],
                    columns=[f"C{j+1}" for j in range(step['costs'].shape[1])]
                )
                st.dataframe(step_df, use_container_width=True)
            st.write("---")
    
    else:
        # For transportation methods, show allocations
        for i, step in enumerate(result['steps']):
            st.write(f"**Step {step['step']}:** {step['description']}")
            
            if 'allocation' in step and np.any(step['allocation'] > 0):
                # Show current allocation
                allocation_df = format_allocation_table(step['allocation'], step.get('costs', result['costs']))
                st.dataframe(allocation_df, use_container_width=True)
                
                # Show remaining supply/demand if available
                if 'remaining_supply' in step or 'remaining_demand' in step:
                    col1, col2 = st.columns(2)
                    if 'remaining_supply' in step:
                        with col1:
                            st.write("**Remaining Supply:**", step['remaining_supply'].tolist())
                    if 'remaining_demand' in step:
                        with col2:
                            st.write("**Remaining Demand:**", step['remaining_demand'].tolist())
            
            st.write("---")


def add_export_functionality(result, problem_type):
    """Add CSV export functionality."""
    
    st.subheader("📥 Export Results")
    
    if st.button("Download Results as CSV"):
        # Prepare data for export
        if problem_type == "Assignment Problem":
            # Export assignment pairs
            export_data = []
            export_data.append(["Assignment Problem Results"])
            export_data.append(["Method", result['method']])
            export_data.append(["Total Cost", result['total_cost']])
            export_data.append([])  # Empty row
            export_data.append(["Worker", "Job", "Cost"])
            
            for i, j in result['assignment']:
                export_data.append([f"Worker {i+1}", f"Job {j+1}", result['costs'][i, j]])
        
        else:
            # Export transportation solution
            allocation = result['allocation']
            costs = result['costs']
            
            export_data = []
            export_data.append(["Transportation Problem Results"])
            export_data.append(["Method", result['method']])
            export_data.append(["Total Cost", result['total_cost']])
            export_data.append([])  # Empty row
            
            # Add allocation matrix
            export_data.append(["Allocation Matrix"])
            # Header row
            header = [""] + [f"D{j+1}" for j in range(allocation.shape[1])] + ["Supply"]
            export_data.append(header)
            
            # Data rows
            for i in range(allocation.shape[0]):
                row = [f"S{i+1}"] + allocation[i, :].tolist()
                if 'supply' in result:
                    row.append(result['supply'][i])
                export_data.append(row)
            
            # Demand row
            if 'demand' in result:
                demand_row = ["Demand"] + result['demand'].tolist() + [""]
                export_data.append(demand_row)
        
        # Convert to CSV string
        output = StringIO()
        writer = csv.writer(output)
        writer.writerows(export_data)
        csv_data = output.getvalue()
        
        st.download_button(
            label="📁 Download CSV",
            data=csv_data,
            file_name=f"transportation_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Transportation Problem Solver",
        page_icon="🚛",
        layout="wide"
    )
    main()
