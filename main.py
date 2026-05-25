from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from sistema.model.veiculo_model import VeiculoModel
from sistema.controller.cancela_controller import CancelaController

cancela_controller = CancelaController()

app = FastAPI(title="Estacionamento MVC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return RedirectResponse("/index.html")


@app.post("/api/veiculos", status_code=201)
async def registrar_veiculo(veiculo: VeiculoModel):
    resultado = cancela_controller.entrada(veiculo)
    if resultado is None:
        raise HTTPException(
            status_code=409,
            detail={"erro": "Veículo já está no estacionamento."},
        )
    return resultado


@app.get("/api/veiculos/{placa}")
async def buscar_veiculo(placa: str):
    resultado = cancela_controller.buscar(placa.upper())
    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail={"erro": "Veículo não encontrado."},
        )
    return resultado


@app.post("/api/pagamento/{placa}")
async def pagar(placa: str):
    resultado = cancela_controller.saida(placa.upper())
    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail={"erro": "Veículo não encontrado."},
        )
    return resultado


app.mount("/", StaticFiles(directory="static", html=True), name="static")
