/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "usart.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
uint8_t jingdudis[23];//��λ��ʾ����
uint8_t wedudis[19];
float jingdu;//��γ��ʵʱλ��
float weidu;
uint8_t directional_sign;//�����־
char* temp[16];
uint8_t ucmd[30];//ָ���
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);

/* USER CODE BEGIN PFP */
int split(char *src,const char *separator,char **dest,int DestLen);
void WiFi_Init(void);
void WiFi_Proc(float j,float w,uint8_t sign);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_TIM2_Init();
  MX_USART1_UART_Init();
  MX_USART2_UART_Init();
  MX_USART3_UART_Init();
  /* USER CODE BEGIN 2 */
	//�����ж�
		__HAL_UART_ENABLE_IT(&huart1, UART_IT_IDLE); 
	HAL_UART_Receive_DMA(&huart1,uart1_data.CommRxBuff,uart1_RX_BUFF_SIZE);
	
		__HAL_UART_ENABLE_IT(&huart2, UART_IT_IDLE); 
	HAL_UART_Receive_DMA(&huart2,uart2_data.CommRxBuff,uart2_RX_BUFF_SIZE);
	
	__HAL_UART_ENABLE_IT(&huart3, UART_IT_IDLE); 
	HAL_UART_Receive_DMA(&huart3,uart3_data.CommRxBuff,uart3_RX_BUFF_SIZE);
	
	WiFi_Init();
	HAL_TIM_Base_Start_IT(&htim2);
  /* USER CODE END 2 */
  
  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
		if(uart1_data.end_flag == 1)//openmv��Ϣ
		{
			uart1_data.end_flag = 0;
			if(uart1_data.rx_len >= 3)//������Ϣ
			{
				if(uart1_data.CommRxBuff[0] == 0xAA && uart1_data.CommRxBuff[2] == 0x55)
				{
					if(uart1_data.CommRxBuff[1] == 0x01)
					{
						directional_sign = 1;
					}
					else if(uart1_data.CommRxBuff[1] == 0x02)
					{
						directional_sign = 2;
					}
					else if(uart1_data.CommRxBuff[1] == 0x00)
					{
						directional_sign = 0;
					}
				}
				else//�Ƿ���Ϣ
				{
						uart1_data.rx_len = 0;
						memset(uart1_data.CommRxBuff, 0, uart1_RX_BUFF_SIZE);	//��ջ�����
				}
				uart1_data.rx_len = 0;
				memset(uart1_data.CommRxBuff, 0, uart1_RX_BUFF_SIZE);	//��ջ�����
			}
			else//�Ƿ�
			{
					uart1_data.rx_len = 0;
					memset(uart1_data.CommRxBuff, 0, uart1_RX_BUFF_SIZE);	//��ջ�����
			}
		}
		if(uart2_data.end_flag == 1)//��λ��Ϣ
		{
			uart2_data.end_flag = 0;
			if(strlen((char*)uart2_data.CommRxBuff) > 45)//������λ
			{
				if(split((char*)uart2_data.CommRxBuff,",",temp,15)==12)
				{
					weidu = atof(temp[3])/100;
					jingdu = atof(temp[5])/100;
				}
					memset(temp, 0, 15);	//��ջ�����
					uart2_data.rx_len = 0;
					memset(uart2_data.CommRxBuff, 0, uart2_RX_BUFF_SIZE);	//��ջ�����
			}
			else//û�ж�λ��
			{
					uart2_data.rx_len = 0;
					memset(uart2_data.CommRxBuff, 0, uart2_RX_BUFF_SIZE);	//��ջ�����
			}
		}
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
		if(flag_500ms == 1)
		{
			flag_500ms = 0;//��������һ��
			WiFi_Proc(jingdu,weidu,directional_sign);//�����ݸ�8266
		}
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */


/**
* @brief  �ָ��ַ���
* @param  src        Դ�ַ���
* @param  separator  �ָ�
* @param  dest       �����Ӵ�������
* @param  DestLen    Ԥ�����ַ�����������
* @retval ʵ�����ַ����ĸ���
* @example split("42,uioj,dk4,56",",",temp,4);  temp[0]=42,...temp[3]=56
**/
int split(char *src,const char *separator,char **dest,int DestLen)
{
	char *pNext;
	int count = 0;
	if (src == NULL || strlen(src) == 0)
		return 0;
	if (separator == NULL || strlen(separator) == 0)
		return 0;
	pNext = (char *)strtok(src,separator);
	while(pNext != NULL) 
	{
		if(dest != NULL)
		*dest++ = pNext;
		++count;
		pNext = (char *)strtok(NULL,separator);
		if(count>=DestLen){
		  break;
		}
	}  
//	*num = count;
	return count;
}


//WiFi ��ʼ��
void WiFi_Init(void)
{
	HAL_Delay(10);
	
	memset(uart3_data.CommRxBuff,0,uart3_RX_BUFF_SIZE);         //�建��

	uart3_data.end_flag = 0;	
	uart3_data.rx_len = 0;	
	
	HAL_UART_Transmit_DMA(&huart3,(unsigned char *)"AT\r\n",4);
	HAL_Delay(200);
	HAL_UART_Transmit_DMA(&huart3,(unsigned char *)"AT+CWMODE=3\r\n", 13);
	HAL_Delay(200);
	HAL_UART_Transmit_DMA(&huart3,(unsigned char *)"AT+CIPMUX=1\r\n", 13);
	HAL_Delay(200);
	HAL_UART_Transmit_DMA(&huart3,(unsigned char *)"AT+CIPSERVER=1,8080\r\n", 21);
	HAL_Delay(200);
	HAL_UART_Transmit_DMA(&huart3,(unsigned char *)"AT+CWSAP_CUR=\"Smarthome1\",\"12345678\",5,3\r\n", 42);
	HAL_Delay(200);
	
	memset(uart3_data.CommRxBuff,0,uart3_RX_BUFF_SIZE);         //�建��

	uart3_data.end_flag = 0;	
	uart3_data.rx_len = 0;	
	
	
	
} 
/*
[23:56:25.326]�ա���$GNRMC,155625.000,A,1141.91877,N,11111.66953,E,0.02,0.00,270424,,,A,V*07
*/
void WiFi_Proc(float j,float w,uint8_t sign)//WIFI�������� ���� γ�� ����
{
	memset(ucmd,0,30);         //�建��
	memset(uart3_data.CommRxBuff,0,uart3_RX_BUFF_SIZE);         //�建��
	
	sprintf((char*)uart3_data.CommTxBuff ,"%3.7f,%2.7f,%d",j,w,sign);
	sprintf((char*)ucmd,"AT+CIPSEND=0,%d\r\n",strlen((char*)uart3_data.CommTxBuff));//ָ��
	HAL_UART_Transmit_DMA(&huart3,(unsigned char *)ucmd, strlen((char*)ucmd));//��ָ��
	HAL_Delay(200);

	HAL_UART_Transmit_DMA(&huart3,uart3_data.CommTxBuff, strlen((char*)uart3_data.CommTxBuff));//������
	HAL_Delay(100);
	
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
