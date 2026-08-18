const bulario = require('bulario');

// Função para buscar o remédio
const buscar = async (nome, pagina = 1, qtd = 6) => {
    try {
        const result = await bulario.buscaFull(nome, pagina, qtd);
        return result;
    } catch (error) {
        throw new Error(error);
    }
};

// Função para obter o PDF da bula pelo ID
const getPdf = async (id) => {
    try {
        const result = await bulario.getPdf(id);
        return result;
    } catch (error) {
        throw new Error(error);
    }
};

// Captura o nome do remédio e a página dos argumentos da linha de comando
const nomeRemedio = process.argv[2];
const pagina = process.argv[3] || 1;

// Executa a busca e a obtenção do PDF
(async () => {
    try {
        // Primeiro, busca o remédio pelo nome
        const resultadoBusca = await buscar(nomeRemedio, pagina);
        
        // Se não encontrar nada, imprime a mensagem e encerra
        if (resultadoBusca.length === 0) {
            console.log(`Nenhum resultado encontrado para: ${nomeRemedio}`);
            return;
        }

        let resultadoPdf = Buffer.from([]); // Criando um buffer vazio para o PDF
        let cont = 0;

        // Verifica se o buffer do PDF é grande o suficiente ou se o tamanho da busca foi atingido (6)
        while (resultadoPdf.length < 200 && cont < resultadoBusca.length - 1) {

            cont += 1;
            // Pegando o ID da bula
            idBula = resultadoBusca[cont].idBulaPacienteProtegido;

            // Obtém o PDF da bula pelo ID
            resultadoPdf = await getPdf(idBula);
        }

        // Se o buffer do PDF for menor que 200, não encontrou o PDF
        if (resultadoPdf.length < 200) {
            resultadoPdf = false;
        }

        // Imprime o resultado da busca e o buffer do pdf
        console.log(JSON.stringify({ busca: resultadoBusca, pdf: resultadoPdf, status: resultadoPdf ? 'found' : 'not_found' }));
        
    } catch (error) {
        console.error(error.message);
    }
})();
