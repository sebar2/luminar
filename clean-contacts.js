const fs = require('fs');
const csv = require('csv-parser');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const inputFile = process.argv[2];
const outputFile = 'C:/Users/sebar/.openclaw/workspace/luminar/Clientes_Luminar_Limpio.csv';

// Female first names that need "Estimada" instead of "Estimado"
const femaleNames = [
    'Francesca', 'Andrea', 'Natalia', 'Maria', 'Carmen', 'Virginia', 'Ivy',
    'María', 'Laura', 'Gabriel', 'Sebastian', 'Carlos', 'Mauricio', 'Juan',
    'Marcos', 'Rodolfo', 'Agustín', 'Eduardo', 'Leonardo', 'Ankin', 'Hernán',
    'Pablo', 'Federico'
];

// Actually, let's be more precise - only fix the known female names
const femaleNamesToFix = [
    'Francesca', 'Andrea', 'Natalia', 'Maria', 'Carmen', 'Virginia', 'Ivy', 'María'
];

function fixGenderInMessage(message, name) {
    if (!message) return message;
    
    // Check if this person's first name is in the female list
    const firstName = name.split(' ')[0];
    if (femaleNamesToFix.includes(firstName)) {
        // Replace "Estimado [Name]" with "Estimada [Name]"
        message = message.replace(new RegExp(`Estimado ${firstName}`, 'g'), `Estimada ${firstName}`);
    }
    
    return message;
}

function fixTitleGreetings(message, name) {
    if (!message) return message;
    
    const firstName = name.split(' ')[0];
    
    // Replace "Hola Ma." with "Hola [firstName]"
    message = message.replace(/Hola Ma\./g, `Hola ${firstName}`);
    // Replace "Hola Arq." with "Hola [firstName]"
    message = message.replace(/Hola Arq\./g, `Hola ${firstName}`);
    // Replace "Hola Ing." with "Hola [firstName]"
    message = message.replace(/Hola Ing\./g, `Hola ${firstName}`);
    
    return message;
}

const results = [];

fs.createReadStream(inputFile)
    .pipe(csv())
    .on('data', (row) => {
        let updatedRow = { ...row };
        const name = updatedRow['Nombre y Apellido'];
        
        // Fix cargo for Carmen Velazco
        if (name === 'Carmen Velazco' && updatedRow['Cargo'] === 'Alvaro') {
            updatedRow['Cargo'] = 'Gerente de Infraestructura';
        }
        
        // Fix gender and title greetings in messages
        if (updatedRow['Mensaje Sugerido']) {
            updatedRow['Mensaje Sugerido'] = fixGenderInMessage(updatedRow['Mensaje Sugerido'], name);
            updatedRow['Mensaje Sugerido'] = fixTitleGreetings(updatedRow['Mensaje Sugerido'], name);
        }
        
        results.push(updatedRow);
    })
    .on('end', () => {
        const csvWriter = createCsvWriter({
            path: outputFile,
            header: [
                {id: 'Nombre y Apellido', title: 'Nombre y Apellido'},
                {id: 'Cargo', title: 'Cargo'},
                {id: 'Empresa', title: 'Empresa'},
                {id: 'Vínculo / Contacto', title: 'Vínculo / Contacto'},
                {id: 'Tel / Web / Email', title: 'Tel / Web / Email'},
                {id: 'Estado / Notas', title: 'Estado / Notas'},
                {id: 'Segmento / Tipo de Cliente', title: 'Segmento / Tipo de Cliente'},
                {id: 'Estado de Contacto', title: 'Estado de Contacto'},
                {id: 'Fecha Próximo Paso', title: 'Fecha Próximo Paso'},
                {id: 'Mensaje Sugerido', title: 'Mensaje Sugerido'}
            ]
        });

        csvWriter.writeRecords(results)
            .then(() => {
                console.log(`Cleaned CSV saved to ${outputFile}`);
            });
    });