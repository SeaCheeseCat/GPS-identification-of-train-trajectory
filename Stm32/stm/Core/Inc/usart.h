/**
  ******************************************************************************
  * @file    usart.h
  * @brief   This file contains all the function prototypes for
  *          the usart.c file
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
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __USART_H__
#define __USART_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

extern UART_HandleTypeDef huart1;
extern UART_HandleTypeDef huart2;
extern UART_HandleTypeDef huart3;

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

void MX_USART1_UART_Init(void);
void MX_USART2_UART_Init(void);
void MX_USART3_UART_Init(void);

/* USER CODE BEGIN Prototypes */
#define uart1_TX_BUFF_SIZE 128
#define uart1_RX_BUFF_SIZE 128

#define uart2_TX_BUFF_SIZE 128
#define uart2_RX_BUFF_SIZE 128


#define uart3_TX_BUFF_SIZE 128
#define uart3_RX_BUFF_SIZE 512

typedef struct
{
	uint16_t tx_cnt;
	uint16_t tx_len;
	uint8_t  CommTxBuff[uart1_TX_BUFF_SIZE];	
	uint16_t rx_cnt;
	uint16_t rx_len;
	uint8_t  CommRxBuff[uart1_RX_BUFF_SIZE];
	uint8_t  end_flag;
}Comm1_t;

typedef struct
{
	uint16_t tx_cnt;
	uint16_t tx_len;
	uint8_t  CommTxBuff[uart2_TX_BUFF_SIZE];	
	uint16_t rx_cnt;
	uint16_t rx_len;
	uint8_t  CommRxBuff[uart2_RX_BUFF_SIZE];
	uint8_t  end_flag;
}Comm2_t;


typedef struct
{
	uint16_t tx_cnt;
	uint16_t tx_len;
	uint8_t  CommTxBuff[uart3_TX_BUFF_SIZE];	
	uint16_t rx_cnt;
	uint16_t rx_len;
	uint8_t  CommRxBuff[uart3_RX_BUFF_SIZE];
	uint8_t  end_flag;
}Comm3_t;

extern Comm1_t uart1_data;//
extern Comm2_t uart2_data;//
extern Comm3_t uart3_data;//
/* USER CODE END Prototypes */

#ifdef __cplusplus
}
#endif

#endif /* __USART_H__ */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
