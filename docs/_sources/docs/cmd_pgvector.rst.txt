.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( pgvector mode )
****************************************************

- List of pgvector mode commands.

Createdb : `witshape -m pgvector -c createdb <Option>`
==============================================================================

- PostgreSQL database creation command for pgvector.
- Install extensions and schemas required for vector searches.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--dbhost <IP address or host name>","","Specify the database host name to connect to."
    "--dbport <port number>","","Specify the database port to connect to."
    "--dbname <db name>","","Specify the name of the database to connect to."
    "--dbuser <db user name>","","Specifies the database user name to connect to."
    "--dbpass <db user password>","","Specify the database password to connect to."
    "--dbtimeout <time-out>","","Specifies the database connection timeout."
    "--newdbname <new db name>","","Specify the name of the database to be created."

Down : `witshape -m pgvector -c down <Option>`
==============================================================================

- Down the pgvector container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "", "", ""

Embedd : `witshape -m pgvector -c embedd <Option>`
==============================================================================

- Reads data and registers embedded values in the database.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--dbhost <IP address or host name>","","Specify the database host name to connect to."
    "--dbport <port number>","","Specify the database port to connect to."
    "--dbname <db name>","","Specify the name of the database to connect to."
    "--dbuser <db user name>","","Specifies the database user name to connect to."
    "--dbpass <db user password>","","Specify the database password to connect to."
    "--dbtimeout <time-out>","","Specifies the database connection timeout."
    "--servicename <servicename>","","Specify the service name."
    "--llmprov <provider>","","Specify llm provider."
    "--llmprojectid <project ID>","","Specify the project ID for llm's provider connection."
    "--llmsvaccountfile <service account file>","","Specifies the service account file for llm's provider connection."
    "--llmlocation <location>","","Specifies the location for llm provider connections."
    "--llmapikey <API key>","","Specify API key for llm provider connection."
    "--llmendpoint <endpoint>","","Specifies the endpoint for llm provider connections."
    "--llmmodel <embedding model>","","Specifies the embedding model for llm."
    "--loadprov <provider>","","Specifies the load provider."
    "--loadpath <path>","","Specifies the load path."
    "--loadgrep <pattern>","","Specifies a load grep pattern."
    "--savetype <type>","","Specify the storage pattern. `per_doc` :per document, `per_service` :per service, `add_only` :add only"
    "--pdf_chunk_table <type>","","Specifies how to chunk tables in the PDF file. `none` :do not chunk by table, `table` :by table, `row_with_header` :by row (with header)"
    "--chunk_size <size>","","Specifies the chunk size."
    "--chunk_overlap <size>","","Specifies the overlap size of the chunk."
    "--chunk_separator <separator>","","Specifies the delimiter character for chunking."

Install : `witshape -m pgvector -c install <Option>`
==============================================================================

- Install the pgvector container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "", "", ""

Search : `witshape -m pgvector -c search <Option>`
==============================================================================

- Search the database using the embedded values of the query.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--dbhost <IP address or host name>","","Specify the database host name to connect to."
    "--dbport <port number>","","Specify the database port to connect to."
    "--dbname <db name>","","Specify the name of the database to connect to."
    "--dbuser <db user name>","","Specifies the database user name to connect to."
    "--dbpass <db user password>","","Specify the database password to connect to."
    "--dbtimeout <time-out>","","Specifies the database connection timeout."
    "--servicename <servicename>","","Specify the service name."
    "--llmprov <provider>","","Specify llm provider."
    "--llmprojectid <project ID>","","Specify the project ID for llm's provider connection."
    "--llmsvaccountfile <service account file>","","Specifies the service account file for llm's provider connection."
    "--llmlocation <location>","","Specifies the location for llm provider connections."
    "--llmapikey <API key>","","Specify API key for llm provider connection."
    "--llmendpoint <endpoint>","","Specifies the endpoint for llm provider connections."
    "--llmmodel <embedding model>","","Specifies the embedding model for llm."
    "--query <prompt>","","Specifies a search query."
    "--kcount <count>","","Specify the number of search results. If filter conditions are specified, the results will be filtered from the number of results specified here."
    "--filter_source <source>","","Specifies the source name of the filter condition. Intermediate match for file paths, etc."
    "--filter_spage <page>","","Specifies the starting page of the filter condition."
    "--filter_epage <page>","","Specifies the end page of the filter condition."
    "--filter_table <table>","","Specifies the table of filter conditions; if True, table elements are targeted."
    "--filter_score <score>","","Specifies the 0~1 score threshold for the filter condition; the closer to 0, the more similar it is."

Uninstall : `witshape -m pgvector -c uninstall <Option>`
==============================================================================

- Uninstall the pgvector container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "", "", ""

up : `witshape -m pgvector -c up <Option>`
==============================================================================

- Up the pgvector container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "", "", ""
