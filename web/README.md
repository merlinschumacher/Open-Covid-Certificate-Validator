## How to change

First, you can serve a develop server as follows.

```bash
npm install
npm run serve
```

Then, you can access to <http://localhost:8080/>, which will be loaded automatically if file changes detected.

You can modify [src/index.ts](src/index.ts) as you want.

## Build

```bash
npm install
npm run build
```

Then, you get `./dist` directory. The file structure should be the following.

```
dist/
├── bundle.js
├── index.html
└── src
    └── index.d.ts
```

`bundle.js` includes an inline source map.
