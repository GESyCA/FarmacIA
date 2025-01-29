const express = require("express");
const fs = require("fs");
const path = require("path");
const bulario = require("bulario");

const app = express();
const PORT = 3000;

// Função para buscar remédios
const buscar = async (nome, pagina = 1, qtd = 6) => {
    try {
        console.log("Buscando remédio...");
        const result = await bulario.buscaFull(nome, pagina, qtd);
        console.log("Resultado da busca:", result[0]);
        return result;
    } catch (error) {
        console.log("Erro:", error);
        throw new Error(error);
    }
};

// Função para obter o PDF da bula pelo ID
const getPdf = async (id) => {
    try {
        return await bulario.getPdf(id);
    } catch (error) {
        throw new Error(error);
    }
};

// Rota para buscar remédios pelo nome
app.get("/buscar/:nome", async (req, res) => {
    const { nome } = req.params;
    const pagina = req.query.pagina || 1;
    console.log(`Buscando remédio: ${nome} na página ${pagina}`);
    try {
        console.log("Buscando...");
        const resultado = await buscar(nome, pagina);
        console.log("Resultado:", resultado[0]);
        if (resultado.length === 0) {
            return res.status(404).json({ message: "Nenhum remédio encontrado" });
        }
        res.json(resultado[0]);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Rota para obter a bula em PDF e baixar localmente
app.get("/bula/:id", async (req, res) => {
    const { id } = req.params;
    const filePath = path.join(__dirname, "bulas", `${id}.pdf`);

    // Se o arquivo já existe, envia direto
    if (fs.existsSync(filePath)) {
        return res.download(filePath);
    }

    try {
        const pdfBuffer = await getPdf(id);
        
        if (pdfBuffer.length < 200) {
            return res.status(404).json({ message: "Bula não encontrada" });
        }

        // Criando diretório se não existir
        if (!fs.existsSync(path.join(__dirname, "bulas"))) {
            fs.mkdirSync(path.join(__dirname, "bulas"));
        }

        // Salvando a bula em PDF localmente
        fs.writeFileSync(filePath, pdfBuffer);

        // Enviando o arquivo para download
        res.download(filePath);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Iniciando o servidor
app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
