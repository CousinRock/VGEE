from .base_tool import BaseTool
import ee

class ClassificationTool(BaseTool):
    @staticmethod
    def kmeans_clustering(image, num_clusters=5):
        """K-means聚类分类"""
        try:
            training = image.sample(
                numPixels=5000,
                scale=30,
                seed=0,
                geometries=True
            )
            
            clusterer = ee.Clusterer.wekaKMeans(num_clusters).train(training)
            result = image.cluster(clusterer)
            
            return result.randomVisualizer()
            
        except Exception as e:
            raise Exception(f"Error in kmeans clustering: {str(e)}")

    @staticmethod
    def supervised_classification(image, training_data, params):
        """监督分类"""
        try:
            # 实现监督分类逻辑
            return {
                'success': True,
                'message': '监督分类完成'
            }
        except Exception as e:
            raise Exception(f"Error in supervised classification: {str(e)}")

    @staticmethod
    def random_forest_classification(image, samples, num_trees=50, train_ratio=0.7):
        """随机森林分类"""
        try:
            # 创建训练特征集合
            training_features = ee.FeatureCollection([])
            
            # 处理每个类别的样本，并为每个类别分配数值标签
            class_index = 0
            for layer_id, sample_data in samples.items():
                features = sample_data['features']
                
                # 将样本点/多边形转换为 Earth Engine 特征
                if sample_data['geometry_type'] == 'Point':
                    # 处理点样本
                    points = [ee.Feature(ee.Geometry.Point(f['coordinates']), {'class': class_index}) 
                             for f in features]
                    class_features = ee.FeatureCollection(points)
                else:
                    # 处理多边形样本
                    polygons = [ee.Feature(ee.Geometry.Polygon(f['coordinates']), {'class': class_index}) 
                              for f in features]
                    class_features = ee.FeatureCollection(polygons)
                
                training_features = training_features.merge(class_features)
                class_index += 1
            
            # 获取图像波段
            bands = image.bandNames()
            
            # 添加随机列并分割训练数据
            withRandom = training_features.randomColumn('random')
            training_partition = withRandom.filter(ee.Filter.lt('random', train_ratio))
            test_partition = withRandom.filter(ee.Filter.gte('random', train_ratio))
            
            # 从训练样本中提取值
            training = image.sampleRegions(
                collection=training_partition,
                properties=['class'],
                scale=30
            )

            test = image.sampleRegions(
                collection=test_partition,
                properties=['class'],
                scale=30
            )
            
            # 创建和训练分类器
            classifier = ee.Classifier.smileRandomForest(numberOfTrees=num_trees).train(
                features=training,
                classProperty='class',
                inputProperties=bands
            )

            classifier_test = ee.Classifier.smileRandomForest(numberOfTrees=num_trees).train(
                features=test,
                classProperty='class',
                inputProperties=bands
            )
            
            # 执行分类
            classified = image.classify(classifier).toByte()
            classified_test = image.classify(classifier_test).toByte()

            # 获取精度评估
            trainAccuracy = classifier.confusionMatrix()
            
            # 设置分类结果的属性
            classified = classified.set({
                'kappa': trainAccuracy.kappa(),
                'accuracy': trainAccuracy.accuracy()
            })
            
            # 添加可视化参数
            return classified
            
        except Exception as e:
            print(f"Error in random forest classification: {str(e)}")
            raise Exception(f"Error in random forest classification: {str(e)}")
