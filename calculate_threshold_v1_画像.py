# -*-coding:utf-8-*-
#-------------------------------------------------------------------------------
# Name:        calculate_threshold
# Purpose:     homework
# Author:      yuma_matsuoka
# Created:     27/10/2015
#-------------------------------------------------------------------------------
import cv2
import pylab as plt
import numpy as np

def varianceCalculate(average, histgram):
    #分散を返す
    variance = 0
    for i in range(len(histgram)):
        variance += (histgram[i] - average) ** 2

    variance /= len(histgram)

    return variance

def averageAndpixelSumCalculate(histgram):
    #平均と画素数の合計を返す
    average = pixelSum = 0
    for i in range(len(histgram)):
        pixelSum += histgram[i]             #ピクセル総数
        brightnessValue = histgram[i] * i   #輝度値の合計

    average = brightnessValue / len(histgram)

    return pixelSum, average

def within_betweenCV(pixelSum1, average1, variance1, pixelSum2, average2, variance2):
    #クラス間分散&クラス内分散を返す

    betweenClassVariance = (pixelSum1 * pixelSum2 * ((average1 - average2) ** 2) ) / ((pixelSum1 + pixelSum2) ** 2)#クラス間分散

    withinClassVariance = (pixelSum1 * variance1 + pixelSum2 * variance2) / (pixelSum1 + pixelSum2)#クラス内分散

    return betweenClassVariance, withinClassVariance

def calculateAll(blackList, whiteList):
    #計算に関する関数を実行
    b_size, b_average = averageAndpixelSumCalculate(blackList)
    w_size, w_average = averageAndpixelSumCalculate(whiteList)

    b_variance = varianceCalculate(b_average, blackList)
    w_variance = varianceCalculate(w_average, whiteList)

    betweenCV, withinCV = within_betweenCV(b_size, b_average, b_variance, w_size, w_average, w_variance)#クラス間分散&クラス内分散

    totalVariance = betweenCV + withinCV#全分散
    separationMetrics = betweenCV / (totalVariance - betweenCV)#クラス間分散とクラス内分散の比：分散度を計算

    return separationMetrics

def main():
    #ファイル読み込み_グレイスケールで読み込み
    image_path = "sample.jpg"                               #読み込む画像の名前
    image = cv2.imread(image_path, 0)                       #画像を読み込んでnumpy型のリストに格納

    #ヒストグラムの作成
    histgram = cv2.calcHist([image], [0], None, [256], [0, 256])

    #分離度を求める
    size = 256
    listSM = [0 for i in range(size)]                       #分離度のリスト listSM=np.zeros(size)
    for i in range(size):
        if i != 0 and i != size-1:
            blackList = histgram[0: i]                      #輝度の小さい方のリスト_blackList
            whiteList = histgram[i: size]                   #輝度の大きい方のリスト_whiteList
            listSM[i] = calculateAll(blackList, whiteList)  #分散度
        elif i == 0 or i == size-1:
            listSM[i] = 0                                   #２つのリストに分けられないときは例外処理

    #最大の分離度から閾値を求める
    maxValue = 0                                            #最大の分離度
    for i in range(size):
        #print("輝度値:", i, "分離度=", listSM[i])            #debug
        if listSM[i] > maxValue:
            maxValue = listSM[i]
            maxValueIndex = i                               #最大の分散度のインデックスを保存
    print("閾値は", maxValueIndex, "です")

    #求めた閾値を基に画像の２値化を行う
    output_otsu = np.zeros((len(image), len(image[0])))    #大津メソッドの出力に使う配列
    for i in range(len(image)):
        for j in range(len(image[0])):
            if image[i][j] > maxValueIndex:
                output_otsu[i][j] = 255                     #閾値より大きいときは255
            else:
                output_otsu[i][j] = 0                       #閾値よりも小さいときは０


    #ヒストグラムの輝度値の真ん中の値を閾値として２値化した画像の作成
    average_histgram = int(len(histgram) / 2)               #ヒストグラムの長さの半分をint型で取得
    output_average = image.copy()                           #単純な２値化による出力に使う配列
    output_average[output_average >= average_histgram] = 255                  #numpyで短く書ける_大きい要素はすべて255
    output_average[output_average < average_histgram] = 0                     #numpyで短く書ける_任意の値より小さい要素はすべてo


    #Adaptive Gaussian Thresholodingを用いた２値化(オプションで追加)
    #引数(２値化するリスト、条件を満たす要素に割り当てる値、閾値決定方法、変換手法、近傍どれくらい見るか、加重平均から引く値)
    aGH = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 89, 7)


    #画像の保存
    cv2.imwrite("gray.jpg", image)                          #グレイスケール
    #cv2.imwrite("average.jpg", output_average)              #静的な閾値使用
    cv2.imwrite("otsu.jpg", output_otsu)                    #大津メソッド
    #cv2.imwrite("Adaptive_Gaussian_Thresholoding.jpg", aGH) #OpenCVの動的な閾値使用

    #画像の表示
    cv2.imshow("input", image)                              #グレイスケール
    cv2.imshow("average", output_average)                   #静的な閾値使用
    cv2.imshow("otsu", output_otsu)                         #大津メソッド
    cv2.imshow("adaptive gaussian", aGH)                    #OpenCVの動的な閾値使用

    #ヒストグラムの出力
    plt.plot(histgram)                                      #ヒストグラムの表示
    #plt.axvline(x=maxValueIndex, color='red', label='otsu') #大津メソッドの閾値表示
    #plt.axvline(x=average_histgram, color='green', label='average')#静的な閾値表示
    plt.legend(loc='upper right')                           #ラベルを表示
    #plt.title("histgram of brightness")                     #タイトル
    #plt.xlabel("brightness")                                #横軸ラベル
    #plt.ylabel("frequency")                                 #縦軸ラベル
    plt.xlim([0, 256])                                      #x軸の範囲設定
    plt.show()

if __name__ == '__main__':
    main()

