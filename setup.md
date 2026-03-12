This printer system does the following:

It prints labels premade designed templates with glabels.

This is setup in a microservices
- vue frontend:
- backend: serves information to the frontend. communicates with the other services in order to generate and print the label.

- glabels-templates: this offers the glabels templates to the backend

- grocy: this fetches all the products in grocy and serves it to the backend
- inventree: this fetches all the storage-locations in inventree and serves it to the frontend.

- label-generator: this takes in a .csv file and .glabels file and returns a .pdf file.

## Flow

1. User opens frontend UI and gets a menu. Here the user gets the option to fetch info from inventree or grocy
2. User chooses grocy. The backend asks the grocy services. grocy service returns all the products to the backend.
3. The user sees a list with all the entries and its properties(provided by grocy service to the backend). The user can choose which products to select by checking checkboxes. there should be a search functionality. when the user click on the button 'next'. the backend sends the info to the csv-generator service. the csv-generator returns the csv to the backend.
4. when the products are selected. the user chooses a template (the backend fetches them from the glabels-templates service)
5. the user presses the button 'generate'. the backend sends the csv and the glabels template to 'label-generator' and gets back a pdf. The generated pdf is shown with an option 'print'.

## services

### Frontend service

This is a vue front-end application that communicates with the backend. It takes in user inputs and shows information to the user

### Backend service

This is the main backend service. It serves and takes in information from and to the frontend and communicates with the other services.

### csv-generator

This service takes information from the backend and returns a csv file

### glabels-template

Serves pre-made glabels templates to the backend

### label-generator

This service takes in the .csv file and the .glabels file and generates a pdf.

### Grocy

Fetches products from the grocy api.

## Getting started

```bash
docker compose up -d
```