// Copia (verbatim, sin modificar) los datos fuente a public/data para que el
// dashboard los sirva. Se ejecuta automáticamente antes de `dev` y `build`.
const fs = require("fs")
const path = require("path")

const root = path.resolve(__dirname, "..")
const repo = path.resolve(root, "..")
const dest = path.join(root, "public", "data")

fs.mkdirSync(dest, { recursive: true })

const copias = [
  [path.join(repo, "dataset_maestro.csv"), path.join(dest, "dataset_maestro.csv")],
  [
    path.join(repo, "6_visualizaciones", "geo", "comunas_caba.geojson"),
    path.join(dest, "comunas_caba.geojson"),
  ],
]

for (const [src, dst] of copias) {
  if (!fs.existsSync(src)) {
    console.error(`[copy-data] No se encontró: ${src}`)
    process.exit(1)
  }
  fs.copyFileSync(src, dst)
  console.log(`[copy-data] ${path.basename(dst)} actualizado`)
}
