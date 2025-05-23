/* filepath: d:\Projects\Code Optimizer\static\js\main.js */
function createASTTree(data, containerId, title) {
    const margin = {top: 20, right: 20, bottom: 20, left: 20};
    const width = 400 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const container = d3.select(containerId)
        .append("div")
        .attr("class", "tree-wrapper");

    container.append("h3")
        .attr("class", "tree-title")
        .text(title);

    const svg = container
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    function transformData(node) {
        if (!node) return null;
        return {
            name: node.value || node.type,
            type: node.type,
            children: (node.left || node.right) ? 
                [
                    node.left && transformData(node.left),
                    node.right && transformData(node.right)
                ].filter(Boolean) : null
        };
    }

    const hierarchicalData = transformData(data);
    const root = d3.hierarchy(hierarchicalData);
    const treeLayout = d3.tree().size([width, height]);
    const treeData = treeLayout(root);

    svg.selectAll(".link")
        .data(treeData.links())
        .join("path")
        .attr("class", "link")
        .attr("d", d3.linkVertical()
            .x(d => d.x)
            .y(d => d.y));

    const nodes = svg.selectAll(".node")
        .data(treeData.descendants())
        .join("g")
        .attr("class", d => `node ${d.data.type.toLowerCase()}`)
        .attr("transform", d => `translate(${d.x},${d.y})`);

    nodes.append("circle")
        .attr("r", 20);

    nodes.append("text")
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .text(d => d.data.name)
        .style("fill", "white")
        .style("font-weight", "bold");
}

// Add this function to display tokens
function displayTokens(expression) {
    const tokensContainer = document.getElementById('tokens-container');
    tokensContainer.innerHTML = '';

    // Split the expression into lines
    const lines = expression.split('\n').filter(line => line.trim());

    lines.forEach((line, index) => {
        // Create a container for this line's tokens
        const lineDiv = document.createElement('div');
        lineDiv.className = 'tokens-line';
        
        // Add line number
        const lineNumber = document.createElement('span');
        lineNumber.className = 'token line-number';
        lineNumber.textContent = `Line ${index + 1}:`;
        lineDiv.appendChild(lineNumber);

        // Tokenize the line
        const tokens = line.match(/\d+|[a-zA-Z]+|[+*/=\-();]/g) || [];
        
        tokens.forEach(token => {
            const tokenSpan = document.createElement('span');
            tokenSpan.className = 'token';
            
            // Add specific class based on token type
            if ('+-*/'.includes(token)) {
                tokenSpan.classList.add('operator');
            } else if ('='.includes(token)) {
                tokenSpan.classList.add('equals');
            } else if (/^\d+$/.test(token)) {
                tokenSpan.classList.add('number');
            } else if (/^[a-zA-Z]+$/.test(token)) {
                tokenSpan.classList.add('identifier');
            }
            
            tokenSpan.textContent = token;
            lineDiv.appendChild(tokenSpan);
        });

        tokensContainer.appendChild(lineDiv);
    });
}

async function optimizeExpression() {
    const expressionInput = document.getElementById('expression');
    const treeContainer = document.getElementById('tree-container');
    const stepsDiv = document.getElementById('steps');
    const resultDiv = document.getElementById('result');
    
    // Clear previous results
    treeContainer.innerHTML = '';
    stepsDiv.innerHTML = '';
    resultDiv.innerHTML = '';
    
    const expression = expressionInput.value.trim();
    if (!expression) {
        alert('Please enter expressions');
        return;
    }

    // Display tokens first
    displayTokens(expression);

    try {
        const response = await fetch('/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ expression: expression })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (!data.asts || !data.steps || !data.variables) {
            throw new Error('Invalid response format from server');
        }

        // Create ASTs for each line
        data.asts.forEach((ast, index) => {
            if (ast) {  // Only create tree if AST exists
                createASTTree(ast, '#tree-container', `Line ${index + 1} AST`);
            }
        });

        // Display steps
        if (data.steps.length > 0) {
            data.steps.forEach((step, index) => {
                const stepElement = document.createElement('div');
                stepElement.className = 'step';
                stepElement.textContent = `Step ${index + 1}: ${step}`;
                stepsDiv.appendChild(stepElement);
            });
        } else {
            stepsDiv.innerHTML = '<div class="step">No optimization steps needed</div>';
        }

        // Display final variable values
        const variablesDiv = document.createElement('div');
        variablesDiv.className = 'variables';
        variablesDiv.innerHTML = '<h3>Final Variable Values:</h3>';
        
        const variables = Object.entries(data.variables);
        if (variables.length > 0) {
            variables.forEach(([name, value]) => {
                const varElement = document.createElement('div');
                varElement.className = 'variable';
                varElement.textContent = `${name} = ${value}`;
                variablesDiv.appendChild(varElement);
            });
        } else {
            variablesDiv.innerHTML += '<div class="variable">No variables defined</div>';
        }
        
        resultDiv.appendChild(variablesDiv);

    } catch (error) {
        console.error('Error:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = `Error: ${error.message}`;
        resultDiv.appendChild(errorDiv);
    }
}

// Add enter key support
document.getElementById('expression').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        optimizeExpression();
    }
});