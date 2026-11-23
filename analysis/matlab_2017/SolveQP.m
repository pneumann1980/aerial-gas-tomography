function [solution, lagrange_multipliers] = SolveQP(A,ppmm,lambda)
    %build the quadratic term
    H = A'*A + lambda*eye(size(A,2));
    %build the linear term
    q = full(-2*ppmm'*A);

    clear model;
    model.A = sparse(eye(size(A,2)));
    model.obj = q;
    model.sense = '>';
    model.rhs = zeros(size(A,2),1);
    %model.lb = zeros(size(A,2),1);
    model.Q = sparse(H);

    clear params;
    params.method = -1;

    result = gurobi(model, params);
    solution = result.x;
    lagrange_multipliers = result.pi;
end