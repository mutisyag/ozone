module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: [
    'plugin:vue/essential',
    '@vue/airbnb',
  ],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'semi': ["error", "never"],
    'func-style': ["error", "expression"],
    'comma-dangle': ["error", "never"],  
    'indent': ["error", "tab"],
    'no-tabs': 'off',
    'no-multiple-empty-lines': ["error", { "max": 1 }],
    'import/extensions': 'off',
    'import/no-mutable-exports': 'off',
    'import/no-unresolved': 'off',    
    'no-param-reassign': 'off',     
    'camelcase': 'off',
    'max-len': 'off',
    'no-unused-expressions': 'off',  
    'arrow-parens': 'off',
    'no-alert': 'off',
    'consistent-return': 'off',
    'radix': 'off',
    'no-prototype-builtins': 'off',
    'no-restricted-syntax': 'off',
    'no-restricted-globals': 'off',
    'no-nested-ternary': 'off',
    'guard-for-in': 'off',
    'dot-notation': 'off',
    'vue/no-use-v-if-with-v-for': 'off',
    'vue/no-side-effects-in-computed-properties': 'off',
  },
  parserOptions: {
    parser: 'babel-eslint',
  },
};
