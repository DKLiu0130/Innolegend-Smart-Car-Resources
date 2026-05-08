#include "uart_fifo.h"
#include <stdio.h>

extern QueueHandle_t uart_frame_queue;  // 由主程序创建

static uint8_t rx_frame_buf[UART_FRAME_MAX_LEN];
static size_t frame_idx = 0;
static uint8_t rx_byte;

void uart_frame_rx_init(void)
{
    frame_idx = 0;
    memset(rx_frame_buf, 0, UART_FRAME_MAX_LEN);
    HAL_UART_Receive_IT(&huart3, &rx_byte, 1);
}
//以上为IOT
//******************//
extern UART_HandleTypeDef huart1;
uint8_t uart_rx_byte; 


uint8_t uart_received_frame[MAX_FRAME_SIZE * 8]; 
uint16_t uart_received_frame_length = 0; 
uint8_t uart_tx_buffer[MAX_FRAME_SIZE + 2];  // ?????
uint16_t uart_tx_length = 0; 

void UART_Init(void) {
    HAL_UART_Receive_IT(&huart1, &uart_rx_byte, 1);
}


// This function is used to deconstruct the received data frame, 
// removing the frame header and footer, and dividing the middle data into bits.
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
	//HAL_GPIO_TogglePin(GPIOD, GPIO_PIN_3);
    if (huart->Instance == USART1) {
        static uint8_t frame_data[MAX_FRAME_SIZE];  // ??????
        static uint16_t frame_index = 0;
        
        if (uart_rx_byte == FRAME_HEADER) {
            frame_index = 0;  // ??????????
        }

        if (frame_index < sizeof(frame_data)) {
            frame_data[frame_index++] = uart_rx_byte;
        }

        if (uart_rx_byte == FRAME_TAIL) {
            uart_received_frame_length = frame_index * 8;  // ?? bit ??

            for (uint16_t i = 0; i < frame_index; i++) {
                uint8_t byte = frame_data[i];
                for (uint8_t bit = 0; bit < 8; bit++) {
                    uart_received_frame[i * 8 + bit] = (byte >> (7 - bit)) & 0x01;
                }
            }

        }
        HAL_UART_Receive_IT(&huart1, &uart_rx_byte, 1);
    }
		if (huart->Instance == USART3) {
			//HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
        if (rx_byte == '\n' || frame_idx >= UART_FRAME_MAX_LEN - 1) {
            rx_frame_buf[frame_idx] = '\0';  // 构建C字符串
						//printf("ok");
            // 发送至队列（建议用静态队列避免分配碎片）
            BaseType_t xHigherPriorityTaskWoken = pdFALSE;
            xQueueSendFromISR(uart_frame_queue, rx_frame_buf, &xHigherPriorityTaskWoken);
            frame_idx = 0;
            memset(rx_frame_buf, 0, UART_FRAME_MAX_LEN);
            portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
        } else if (rx_byte != '\r') {  // 忽略回车
            rx_frame_buf[frame_idx++] = rx_byte;
        }
        // 继续接收下一个字节
        HAL_UART_Receive_IT(&huart3, &rx_byte, 1);
    }
}

void UART_SendFrame(uint8_t *bit_data, uint16_t bit_length) {
    if (bit_length % 8 != 0) {
        printf("Error: Bit length must be a multiple of 8!\n");
        return;
    }

    uint16_t byte_length = bit_length / 8;  

    uart_tx_buffer[0] = FRAME_HEADER;

    for (uint16_t i = 0; i < byte_length; i++) {
        uart_tx_buffer[i + 1] = 0;
        for (uint8_t k = 0; k < 8; k++) {
            uart_tx_buffer[i + 1] |= (bit_data[i * 8 + k] & 0x01) << (7 - k);
        }
    }

    uart_tx_buffer[byte_length + 1] = FRAME_TAIL;

    uart_tx_length = byte_length + 2;

    HAL_UART_Transmit_IT(&huart1, uart_tx_buffer, uart_tx_length);
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        printf("UART Transmission Complete!\n");
    }
}
