import boto3
import csv
import os
from datetime import datetime, timedelta

# Configurações
aws_region = "us-east-1"
s3_bucket_name = "analisecontas98"

# Inicializar boto3
session = boto3.Session()
ce_client = session.client('ce', region_name=aws_region)
s3_client = session.client('s3')

def get_cost_report(start_date, end_date):
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Chamada para agrupar por SERVICE
    response_service = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date_str,
            'End': end_date_str
        },
        Granularity='MONTHLY',
        Metrics=['BlendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )
    
    # Chamada para agrupar por USAGE_TYPE
    response_usage_type = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date_str,
            'End': end_date_str
        },
        Granularity='MONTHLY',
        Metrics=['BlendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'USAGE_TYPE'
            }
        ]
    )
    
    return response_service, response_usage_type

def generate_csv_report(service_data, usage_data, file_name):
    with open(file_name, 'w', newline='') as csvfile:
        fieldnames = ['Type', 'Key', 'Amount', 'Unit']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        
        # Adiciona os dados do serviço ao CSV
        for result in service_data['ResultsByTime']:
            for group in result['Groups']:
                writer.writerow({
                    'Type': 'Service',
                    'Key': group['Keys'][0],
                    'Amount': group['Metrics']['BlendedCost']['Amount'],
                    'Unit': group['Metrics']['BlendedCost']['Unit'],
                })
        
        # Adiciona os dados de tipo de uso ao CSV
        for result in usage_data['ResultsByTime']:
            for group in result['Groups']:
                writer.writerow({
                    'Type': 'UsageType',
                    'Key': group['Keys'][0],
                    'Amount': group['Metrics']['BlendedCost']['Amount'],
                    'Unit': group['Metrics']['BlendedCost']['Unit'],
                })

def upload_to_s3(file_name, bucket_name):
    try:
        s3_client.upload_file(file_name, bucket_name, file_name)
        print(f"Arquivo {file_name} enviado para o bucket {bucket_name}.")
    except Exception as e:
        print(f"Erro ao enviar o arquivo para o S3: {e}")

if __name__ == "__main__":
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    service_data, usage_data = get_cost_report(start_date, end_date)
    
    csv_file_name = "aws_cost_report.csv"
    generate_csv_report(service_data, usage_data, csv_file_name)
    
    # Faz o upload do arquivo CSV para o S3
    upload_to_s3(csv_file_name, s3_bucket_name)

    print(f"Relatório de custos gerado: {csv_file_name}")
