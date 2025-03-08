from .base_tool import BaseTool
from services.map_service import get_dataset
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
            
            return result
            
        except Exception as e:
            raise Exception(f"Error in kmeans clustering: {str(e)}")


    @staticmethod
    def random_forest_classification(image, samples, num_trees=50, train_ratio=0.7):
        """随机森林分类"""
        try:
            # 创建训练特征集合
            training_features = ee.FeatureCollection([])
            
            print("Debug - Samples:", samples)  # 添加调试信息
            
            # 处理每个类别的样本，并为每个类别分配数值标签
            class_index = 0
            for layer_id, sample_data in samples.items():
                features = sample_data['features']
                class_name = sample_data['class_name']  # 获取类别名称
                
                print(f"Debug - Processing class {class_name} with index {class_index}")  # 添加调试信息
                
                # 将样本点/多边形转换为 Earth Engine 特征
                if sample_data['geometry_type'] == 'Point':
                    # 处理点样本
                    points = []
                    for f in features:
                        # 创建带有类别属性的特征
                        point = ee.Feature(
                            ee.Geometry.Point(f['coordinates']),
                            {'class': class_index}
                        )
                        points.append(point)
                    class_features = ee.FeatureCollection(points)
                    
                elif sample_data['geometry_type'] == 'Vector':
                    # 处理矢量数据
                    data = get_dataset(layer_id)
                    vector_fc = data if data else ee.FeatureCollection(layer_id)
                    # vector_fc = ee.FeatureCollection(layer_id)
                    class_features = vector_fc.map(lambda f: f.set('class', class_index))
                    
                else:
                    # 处理多边形样本
                    polygons = []
                    for f in features:
                        # 创建带有类别属性的特征
                        polygon = ee.Feature(
                            ee.Geometry.Polygon(f['coordinates']),
                            {'class': class_index}
                        )
                        polygons.append(polygon)
                    class_features = ee.FeatureCollection(polygons)
                
                print(f"Debug - Created features for class {class_name}")  # 添加调试信息
                
                training_features = training_features.merge(class_features)
                class_index += 1
            
            print("Debug - Total training features:", training_features.size().getInfo())  # 添加调试信息
            
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
            # 先设置精度属性
            classified = classified.set({
                'kappa': trainAccuracy.kappa(),
                'accuracy': trainAccuracy.accuracy()
            })
            
            
            return classified
            
        except Exception as e:
            print(f"Error in random forest classification: {str(e)}")
            raise Exception(f"Error in random forest classification: {str(e)}")

    @staticmethod
    def svm_classification(image, samples, kernel='RBF', train_ratio=0.7):
        """支持向量机分类
        Args:
            image: 输入影像
            samples: 训练样本
            kernel: 核函数类型 ('RBF', 'LINEAR')
            train_ratio: 训练集比例
        """
        try:
            # 创建训练特征集合
            training_features = ee.FeatureCollection([])
            
            # 处理每个类别的样本
            class_index = 0
            for layer_id, sample_data in samples.items():
                features = sample_data['features']
                class_name = sample_data['class_name']
                
                # 将样本转换为 Earth Engine 特征
                if sample_data['geometry_type'] == 'Point':
                    points = []
                    for f in features:
                        point = ee.Feature(
                            ee.Geometry.Point(f['coordinates']),
                            {'class': class_index}
                        )
                        points.append(point)
                    class_features = ee.FeatureCollection(points)
                    
                elif sample_data['geometry_type'] == 'Vector':
                    vector_fc = ee.FeatureCollection(layer_id)
                    class_features = vector_fc.map(lambda f: f.set('class', class_index))
                    
                else:
                    polygons = []
                    for f in features:
                        polygon = ee.Feature(
                            ee.Geometry.Polygon(f['coordinates']),
                            {'class': class_index}
                        )
                        polygons.append(polygon)
                    class_features = ee.FeatureCollection(polygons)
                
                training_features = training_features.merge(class_features)
                class_index += 1
                
            # 获取图像波段
            bands = image.bandNames()
            
            # 分割训练和测试数据
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
            classifier = ee.Classifier.libsvm(kernelType=kernel).train(
                features=training,
                classProperty='class',
                inputProperties=bands
            )
            
            # 执行分类
            classified = image.classify(classifier).toByte()
            
            # 获取精度评估
            trainAccuracy = classifier.confusionMatrix()
            
            
            # 设置分类结果的属性
            classified = classified.set({
                'kappa': trainAccuracy.kappa(),
                'accuracy': trainAccuracy.accuracy()
            })
            
            return classified
            
        except Exception as e:
            print(f"Error in SVM classification: {str(e)}")
            raise Exception(f"Error in SVM classification: {str(e)}")
